import logging

from django.core.paginator import Paginator
from django.db.models import Q, Count

from GuideToExile.models import BuildGuide

logger = logging.getLogger('guidetoexile')


def find_with_filter(filter_form, user_id, page, paginate_by):
    queryset = BuildGuide.objects.defer('pob_details')
    base_filters = _get_base_filters(filter_form, user_id)
    queryset = queryset.filter(*base_filters)
    queryset = _filter_keystones(queryset, filter_form)
    queryset = _filter_unique_items(queryset, filter_form)
    queryset = queryset.order_by('creation_datetime').reverse().all()
    logger.debug('Search query=%s', queryset.query)
    page_obj = _get_page(page, paginate_by, queryset)
    return page_obj


def find_all(page, paginate_by):
    queryset = BuildGuide.objects.defer('pob_details').all()
    return _get_page(page, paginate_by, queryset)


def _get_page(page, paginate_by, queryset):
    paginator = Paginator(queryset, paginate_by)
    page_obj = paginator.get_page(page)
    return page_obj


def _filter_keystones(queryset, filter_form):
    keystone_keys = filter_form.cleaned_data['keystones']
    if keystone_keys:
        keystone_choices = dict(filter_form.fields['keystones'].choices)
        keystones = [keystone_choices[int(keystone_key)] for keystone_key in keystone_keys]
        queryset = queryset.filter(keystones__name__in=keystones)
        queryset = queryset.annotate(num_keystones=Count('keystones'))
        queryset = queryset.filter(num_keystones=len(keystones))
    return queryset


def _filter_unique_items(queryset, filter_form):
    unique_item_keys = filter_form.cleaned_data['unique_items']
    if unique_item_keys:
        unique_item_choices = dict(filter_form.fields['unique_items'].choices)
        unique_items = [unique_item_choices[int(unique_item_key)] for unique_item_key in unique_item_keys]
        queryset = queryset.filter(unique_items__name__in=unique_items)
        queryset = queryset.annotate(num_unique_items=Count('unique_items'))
        queryset = queryset.filter(num_unique_items=len(unique_items))
    return queryset


def _get_base_filters(filter_form, user_id):
    data = filter_form.cleaned_data
    filters = [
        Q(title__icontains=data['title']),
        Q(author__user__username__icontains=data['author_username']),
        Q(modification_datetime__gte=data['updated_after']),
    ]
    if data['base_class_name'] != '0':
        filters.append(Q(ascendancy_class__base_class_name=data['base_class_name']))
    if data['asc_class_name'] != '0':
        filters.append(Q(ascendancy_class__name=data['asc_class_name']))

    if user_id != 0:
        liked = data['liked_by_me']
        if liked is True:
            filters.append(Q(guidelike__user__user_id=user_id) & Q(guidelike__is_active=True))
        if liked is False:
            filters.append(~Q(guidelike__user__user_id=user_id) | Q(guidelike__is_active=False))

    if (value := int(data['active_skill'])) != 0:
        skill_name = dict(filter_form.fields['active_skill'].choices)[value]
        filters.append(Q(primary_skills__name=skill_name))
    return filters
