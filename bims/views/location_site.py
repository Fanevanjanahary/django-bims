from django.views.generic import TemplateView, View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import reverse
from django.contrib.gis.geos import Point
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404

from bims.utils.get_key import get_key
from bims.enums.geomorphological_zone import (
    GEOMORPHOLOGICAL_ZONE_CATEGORY_ORDER
)
from bims.models import (
    LocationSite, LocationType, LocationContext, LocationContextGroup,
    SiteImage, Survey, ChemicalRecord
)
from sass.models import River
from bims.utils.jsonify import json_loads_byteified
from bims.serializers.survey_serializer import SurveySerializer


class LocationSiteFormView(TemplateView):
    template_name = 'location_site_form_view.html'
    success_message = 'New site has been successfully added'

    def update_or_create_location_site(self, post_dict):
        location_site = LocationSite.objects.create(**post_dict)
        return location_site

    def additional_context_data(self):
        return {
            'username': self.request.user.username,
            'user_id': self.request.user.id
        }

    def check_site_images(self, location_site):
        site_image_file = self.request.FILES.get('site-image', None)
        if location_site:
            if site_image_file:
                SiteImage.objects.get_or_create(
                    site=location_site,
                    image=site_image_file
                )
        site_image_to_delete = self.request.POST.get(
            'id_site_image_delete', None)
        if site_image_to_delete:
            try:
                SiteImage.objects.get(id=site_image_to_delete).delete()
            except SiteImage.DoesNotExist:
                pass


    def get_context_data(self, **kwargs):
        context = super(LocationSiteFormView, self).get_context_data(**kwargs)
        context['geoserver_public_location'] = get_key(
            'GEOSERVER_PUBLIC_LOCATION')
        context['geomorphological_zone_category'] = [
            (g.name, g.value) for g in GEOMORPHOLOGICAL_ZONE_CATEGORY_ORDER
        ]
        if self.request.user.get_full_name():
            context['fullname'] = self.request.user.get_full_name()
        else:
            context['fullname'] = self.request.user.username
        context['user_id'] = self.request.user.id
        context.update(self.additional_context_data())
        return context

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return super(LocationSiteFormView, self).get(request, *args, **kwargs)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        owner = request.POST.get('owner', '').strip()
        if not owner:
            owner = None
        latitude = request.POST.get('latitude', None)
        longitude = request.POST.get('longitude', None)
        legacy_site_code = request.POST.get('legacy_site_code', '')
        refined_geomorphological_zone = request.POST.get(
            'refined_geomorphological_zone',
            None
        )
        river_name = request.POST.get('river_name', None)
        original_river_name = request.POST.get('original_river_name', '')
        if not river_name:
            river_name = original_river_name

        site_code = request.POST.get('site_code', None)
        site_description = request.POST.get('site_description', None)
        catchment_geocontext = request.POST.get('catchment_geocontext', None)
        geomorphological_group_geocontext = request.POST.get(
            'geomorphological_group_geocontext',
            None
        )

        if not latitude or not longitude or not site_code:
            raise Http404()

        latitude = float(latitude)
        longitude = float(longitude)

        if owner:
            try:
                owner = get_user_model().objects.get(
                    id=owner
                )
            except (get_user_model().DoesNotExist, ValueError):
                raise Http404('User does not exist')

        river, river_created = River.objects.get_or_create(
            name=river_name,
            owner=owner
        )

        geometry_point = Point(longitude, latitude)
        location_type, status = LocationType.objects.get_or_create(
            name='PointObservation',
            allowed_geometry='POINT'
        )
        post_dict = {
            'name': site_code,
            'owner': owner,
            'latitude': latitude,
            'longitude': longitude,
            'river': river,
            'site_description': site_description,
            'geometry_point': geometry_point,
            'location_type': location_type,
            'site_code': site_code,
            'legacy_river_name': original_river_name,
            'legacy_site_code': legacy_site_code
        }
        location_site = self.update_or_create_location_site(
            post_dict
        )

        # Flag to indicate new geomorphological data has been
        # fetched from geocontext
        geomorphological_fetched = False
        if geomorphological_group_geocontext:
            geomorphological_data = json_loads_byteified(
                geomorphological_group_geocontext
            )
            for registry in geomorphological_data['service_registry_values']:
                if 'key' in registry and 'name' in registry:
                    group, group_created = (
                        LocationContextGroup.objects.get_or_create(
                            key=registry['key'],
                            name=registry['name'],
                            geocontext_group_key=geomorphological_data['key']
                        )
                    )
                    LocationContext.objects.get_or_create(
                        site=location_site,
                        value=registry['value'],
                        group=group
                    )
                    geomorphological_fetched = True
                else:
                    LocationContext.objects.filter(
                        site=location_site,
                        group__geocontext_group_key=geomorphological_data[
                            'key']
                    ).delete()

        try:
            if catchment_geocontext:
                catchment_data = json_loads_byteified(
                    catchment_geocontext
                )
                if 'service_registry_values' in catchment_data:
                    for registry in catchment_data['service_registry_values']:
                        if not registry['value']:
                            continue
                        group, group_created = (
                            LocationContextGroup.objects.get_or_create(
                                key=registry['key'],
                                name=registry['name'],
                                geocontext_group_key=catchment_data['key']
                            )
                        )
                        LocationContext.objects.get_or_create(
                            site=location_site,
                            value=registry['value'],
                            group=group
                        )
        except TypeError:
            pass

        if refined_geomorphological_zone:
            location_site.refined_geomorphological = (
                refined_geomorphological_zone
            )
        else:
            if location_site.refined_geomorphological:
                location_site.refined_geomorphological = ''

        geo_class = LocationContext.objects.filter(
            site=location_site,
            group__key='geo_class_recoded'
        )
        if not location_site.creator:
            location_site.creator = self.request.user
        # Set original_geomorphological
        if geo_class.exists():
            if geomorphological_fetched:
                location_site.original_geomorphological = (
                    geo_class[0].value
                )
        else:
            if not location_site.original_geomorphological:
                location_site.original_geomorphological = (
                    refined_geomorphological_zone
                )
        location_site.save()

        self.check_site_images(location_site)

        messages.success(
            self.request,
            self.success_message,
            extra_tags='location_site_form'
        )

        return HttpResponseRedirect(
            '{url}?id={id}'.format(
                url=reverse('location-site-update-form'),
                id=location_site.id
            )
        )


class LocationSiteFormUpdateView(LocationSiteFormView):

    location_site = None
    success_message = 'Site has been successfully updated'

    def update_or_create_location_site(self, post_dict):
        # Update current location context document
        LocationSite.objects.filter(
            id=self.location_site.id
        ).update(
            **post_dict
        )
        return LocationSite.objects.get(id=self.location_site.id)

    def additional_context_data(self):
        context_data = dict()
        context_data['location_site_lat'] = self.location_site.latitude
        context_data['location_site_long'] = self.location_site.longitude
        context_data['site_code'] = self.location_site.site_code
        context_data['site_description'] = self.location_site.site_description
        context_data['refined_geo_zone'] = (
            self.location_site.refined_geomorphological
        )
        context_data['original_geo_zone'] = (
            self.location_site.original_geomorphological
        )
        context_data['site_identifier'] = (
            self.location_site.location_site_identifier
        )
        context_data['update'] = True
        context_data['allow_to_edit'] = self.allow_to_edit()
        context_data['site_id'] = self.location_site.id
        context_data['legacy_site_code'] = self.location_site.legacy_site_code
        context_data['legacy_river_name'] = (
            self.location_site.legacy_river_name
        )
        context_data['site_image'] = SiteImage.objects.filter(
            site=self.location_site
        )

        if (
                ChemicalRecord.objects.filter(
                    survey__site=self.location_site
                ).exists()):
            context_data['surveys'] = SurveySerializer(
                Survey.objects.filter(
                    site_id=self.location_site,
                    chemical_collection_record__isnull=False
                ).distinct().order_by('date'), many=True
            ).data

        if self.location_site.owner:
            context_data['fullname'] = self.location_site.owner.get_full_name()
            context_data['user_id'] = self.location_site.owner.id
        elif self.location_site.creator:
            context_data['fullname'] = (
                self.location_site.creator.get_full_name()
            )
            context_data['user_id'] = self.location_site.creator.id
        else:
            context_data['fullname'] = ''
            context_data['user_id'] = ''
        if self.location_site.river:
            context_data['river_name'] = self.location_site.river.name
        return context_data

    def allow_to_edit(self):
        """Check if user is allowed to update the data"""
        if self.request.user.is_superuser:
            return True
        if self.location_site.owner:
            if self.request.user.id == self.location_site.owner.id:
                return True
        if self.location_site.creator:
            if self.request.user.id == self.location_site.creator.id:
                return True
        return False

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        location_site_id = self.request.GET.get('id', None)
        if not location_site_id:
            raise Http404('Need location site id')
        try:
            self.location_site = LocationSite.objects.get(id=location_site_id)
        except LocationSite.DoesNotExist:
            raise Http404('Location site does not exist')
        return super(LocationSiteFormUpdateView, self).get(
            request, *args, **kwargs)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        # Check if user is the creator of the site or superuser
        location_site_id = self.request.POST.get('id', None)
        if not location_site_id:
            raise Http404('Need location site id')
        try:
            self.location_site = LocationSite.objects.get(id=location_site_id)
        except LocationSite.DoesNotExist:
            raise Http404('Location site does not exist')
        if not self.allow_to_edit():
            raise Http404()
        return super(LocationSiteFormUpdateView, self).post(
            request, *args, **kwargs
        )


class LocationSiteFormDeleteView(UserPassesTestMixin, View):
    location_site = None

    def test_func(self):
        if self.request.user.is_anonymous:
            return False
        if self.request.user.is_superuser:
            return True
        location_site_id = self.kwargs.get('site_id', None)
        if not location_site_id:
            return False
        try:
            self.location_site = LocationSite.objects.get(
                id=location_site_id
            )
        except LocationSite.DoesNotExist:
            return False
        if self.location_site.creator:
            if self.request.user.id == self.location_site.creator.id:
                return True
        if self.location_site.owner:
            if self.request.user.id == self.location_site.owner.id:
                return True
        return False

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        location_site = get_object_or_404(
            LocationSite,
            id=self.kwargs.get('site_id', None)
        )
        location_site.delete()
        messages.success(
            self.request,
            'Location site successfully deleted',
            extra_tags='location_site_form'
        )
        return HttpResponseRedirect(reverse('location-site-form'))
