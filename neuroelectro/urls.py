from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('neuroelectro.views',
    url(r'^accounts/login/$', 'login'),
    url(r'^accounts/logout/$', 'logout'),
    url(r'^admin_list_email/$', 'admin_list_email'),
    url(r'^$', 'splash_page'),
    url(r'^neuron/index/$', 'neuron_index'),
    url(r'^neuron/(?P<neuron_id>\d+)/$', 'neuron_detail'),
    url(r'^neuron/(?P<neuron_id>\d+)/data/$', 'neuron_data_detail'),
    url(r'^ephys_prop/(?P<ephys_prop_id>\d+)/data/$', 'ephys_data_detail'),
    url(r'^ephys_prop/index/$', 'ephys_prop_index'),
    url(r'^ephys_prop/(?P<ephys_prop_id>\d+)/$', 'ephys_prop_detail'),
    url(r'^data_table/(?P<data_table_id>\d+)/$', 'data_table_detail'),
    url(r'^data_table/(?P<data_table_id>\d+)/no_annotation/$', 'data_table_detail_no_annotation'),
    url(r'^article/(?P<article_id>\d+)/$', 'article_detail'),
    url(r'^article_full_text/(?P<article_id>\d+)/$', 'article_full_text_detail'),
    url(r'^article/(?P<article_id>\d+)/metadata/$', 'article_metadata'),
    url(r'^ephys_concept_map/(?P<ephys_concept_map_id>\d+)/$', 'ephys_concept_map_detail'),
    url(r'^ephys_concept_map/mod/$', 'ephys_concept_map_modify'),
    url(r'^neuron_concept_map/mod/$', 'neuron_concept_map_modify'),
    url(r'^neuron/add/$', 'neuron_add'),
    # url(r'^data_table/(?P<data_table_id>\d+)/remove/$', 'data_table_validate_all'),
	url(r'^article/index/$', 'article_list'),
    url(r'^article/metadata_index/$', 'article_metadata_list'),
    url(r'^display_meta/$', 'display_meta'),
    url(r'^neuron_search_form/$', 'neuron_search_form'),
    url(r'^neuron_search_form/neuron_search/$', 'neuron_search'),
    url(r'^neuron/clustering/$', 'neuron_clustering'),
    url(r'^faqs/$', 'faqs'),
    url(r'^contact_info/$', 'contact_info'),
    #@url(r'^api/$', 'api'),
    url(r'^api/docs/$', 'api_docs'),
    url(r'^contribute/$', 'contribute'),
    url(r'^unsubscribe/$', 'unsubscribe'),
    url(r'^publications/$', 'publications'),
    #url(r'^api/neuron_list/$', 'nlex_neuron_id_list'),
    url(r'^ephys_prop/ontology/$', 'ephys_prop_ontology'),
    #url(r'^data_table/(?P<data_table_id>\d+)/validate/view/$', 'data_table_detail_validate'),

    url(r'^neuron_data_add/$', 'neuron_data_add'),

    url(r'^mailing_list_form/$', 'mailing_list_form'),
    url(r'^mailing_list_form_post/$', 'mailing_list_form_post'),
    url(r'^nedm_comment_box/$', 'nedm_comment_box'),
    url(r'^weblog/', include('zinnia.urls')),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^ckeditor/', include('ckeditor.urls')),
    
    # for curation interface
    url(r'^curator_view/$', 'curator_view'),
    url(r'^data_table/validate_list/$', 'data_table_to_validate_list'),
    url(r'^data_table/expert_list/$', 'data_table_expert_list'),
    url(r'^data_table/no_neuron_list/$', 'data_table_no_neuron_list'),
    
    # for asking someone to become a curator
    url(r'^neuron/(?P<neuron_id>\d+)/curate_list/$', 'neuron_article_curate_list'),
    url(r'^neuron/(?P<neuron_id>\d+)/curator_ask/$', 'neuron_curator_ask'),
    url(r'^neuron/(?P<neuron_id>\d+)/become_curator/$', 'neuron_become_curator'),
    
    # suggesting articles for curation 
    url(r'^neuron/(?P<neuron_id>\d+)/article_suggest/$', 'neuron_article_suggest'),
    url(r'^neuron/(?P<neuron_id>\d+)/article_suggest_post/$', 'neuron_article_suggest_post'),
    url(r'^article_suggest/$', 'article_suggest'),
    url(r'^article_suggest_post/$', 'article_suggest_post'),
)

