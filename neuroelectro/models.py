# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 10:55:20 2012

@author: Shreejoy
"""
from django.db import models
from django.contrib.auth.models import AbstractUser as auth_user
from django_localflavor_us import us_states
from db_functions import countries
from picklefield.fields import PickledObjectField
from django.db.models import Q

#  Constants
VALID_JOURNAL_NAMES = ['Brain Research', 'Neuroscience letters', 'Neuron', 'Molecular and cellular neurosciences',
                        'Neuroscience', 'Neuropsychologia', 'Neuropharmacology' 'Brain research bulletin', 
                        'Biophysical Journal', 'Biophysical reviews and letters',
                        'Journal of Neuroscience Research', 'Hippocampus', 'Glia', 'The European journal of neuroscience', 'Synapse (New York, N.Y.)',
                        'The Journal of Physiology', 'Epilepsia',
                        'The Journal of neuroscience : the official journal of the Society for Neuroscience', 'Journal of neurophysiology']  

class API(models.Model):
    path = models.CharField(max_length=200)
    ip = models.GenericIPAddressField()
    time = models.DateTimeField(auto_now=False, auto_now_add=True)
    def __str__(self):
        return u'%s , %s , %s' % (self.ip, self.path, self.time)

# Some of the fields here may be automatically determined by IP address.  
class Institution(models.Model): 
    name = models.CharField(max_length=200) # e.g. Carnegie Mellon University
    type = models.CharField(max_length=50,choices=(('edu','University'),('org','Institute'),('com','Industry'),('gov','Government')), null=True)
    country = models.CharField(max_length=50,choices=countries.COUNTRIES, null=True)
    state = models.CharField(max_length=2,choices=us_states.STATE_CHOICES, null=True)
    def __str__(self):
        return u'%s' % self.name

# Subclass of Django's user class, with extra fields added.  
class User(auth_user):
    institution = models.ForeignKey('Institution', null=True, blank=True)
    lab_head = models.CharField(max_length=50, null=True, blank=True)
    lab_website_url  = models.CharField(max_length = 200, null=True, blank=True)
    assigned_neurons = models.ManyToManyField('Neuron', null=True, blank=True)
    last_update = models.DateTimeField(auto_now = True, null = True, blank=True)
    is_curator = models.BooleanField(default = False)
    #objects = auth_user.objects # Required to use this model with social_auth. 
    
def get_robot_user():
    return User.objects.get_or_create(username = 'robot', first_name='robot', last_name='')[0]
    
def get_anon_user():
    return User.objects.get_or_create(username = 'anon', first_name='Anon', last_name='User')[0]
    
class MailingListEntry(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length = 200, null=True)
    comments = models.CharField(max_length = 500, null=True)
    def __str__(self):
        return u'%s' % self.email

########## Allen Stuff ##############

class Protein(models.Model): # class for gene-coding proteins
    gene = models.CharField(max_length=20)
    name = models.CharField(max_length=400)
    common_name = models.CharField(max_length=400, null = True) # this is to accomadate chan names
    synonyms = models.ManyToManyField('ProteinSyn', null = True)
    allenid =  models.IntegerField()
    entrezid =  models.IntegerField(null=True)    
    in_situ_expts = models.ManyToManyField('InSituExpt', null = True)
    is_channel = models.BooleanField(default = False)
#   go_terms = models.ManyToManyField('GOTerm', null = True)

    def __unicode__(self):
        return u'%s' % self.gene  

class InSituExpt(models.Model):
    imageseriesid = models.IntegerField()
    plane = models.CharField(max_length=20)
    valid = models.BooleanField(default = True)
    regionexprs = models.ManyToManyField('RegionExpr', null = True)
     
    def __unicode__(self):
        return u'%s' % (self.imageseriesid)

class BrainRegion(models.Model):
    name = models.CharField(max_length=500)
    abbrev = models.CharField(max_length=10)
    isallen = models.BooleanField(default = False)
    allenid = models.IntegerField(default = 0, null = True)
    treedepth = models.IntegerField(null = True)
    color = models.CharField(max_length=10, null = True)    
    
    def __unicode__(self):
        return self.name

class RegionExpr(models.Model):
    region = models.ForeignKey('BrainRegion', default = 0)
    expr_energy = models.FloatField(null=True)
    expr_density = models.FloatField(null=True)
    expr_energy_cv = models.FloatField(null=True)
    def __unicode__(self):
        return u'%s' % self.expr_energy
        
class ProteinSyn(models.Model):
    term = models.CharField(max_length=500)
    def __unicode__(self):
        return self.term    
        
class Neuron(models.Model):
    name = models.CharField(max_length=500)
    synonyms = models.ManyToManyField('NeuronSyn', null=True)
    nlex_id = models.CharField(max_length=100, null = True) #this is the nif id
    regions = models.ManyToManyField('BrainRegion', null=True)
    neuron_db_id = models.IntegerField(null=True) # this is the id mapping to NeuronDB
    #defining_articles = models.ManyToManyField('Article', null=True)
    date_mod = models.DateTimeField(auto_now = True, null = True)
    added_by = models.CharField(max_length = 20, null=True)
    # proposed change: add a self-referential field parent to indicate that this neuron is a subtype

    def __unicode__(self):
        return self.name

class NeuronSyn(models.Model):
    term = models.CharField(max_length=500)
    def __unicode__(self):
        return self.term

class EphysProp(models.Model):
    name = models.CharField(max_length=200)
    units = models.ForeignKey('Unit',null=True)
    nlex_id = models.CharField(max_length=100, null = True) #this is the nif id
    synonyms = models.ManyToManyField('EphysPropSyn')
    definition = models.CharField(max_length=1000, null=True) # some def of property
    norm_criteria = models.CharField(max_length=1000, null=True) # indicates how normalized

    def __unicode__(self):
        return u'%s' % self.name
        
class EphysPropSyn(models.Model):
    term = models.CharField(max_length=200)
    
    def __unicode__(self):
        return u'%s' % self.term
        
class Journal(models.Model):
    title = models.CharField(max_length=300)
    short_title = models.CharField(max_length=100, null=True)
    publisher = models.ForeignKey('Publisher',null=True)
    
    def __unicode__(self):
        return self.title

    # indicates whetehr currently indexing journal in DB as full-text journal
    def is_full_text_journal(self):
        if self.title in VALID_JOURNAL_NAMES:
            return True
        else:
            return False

class Publisher(models.Model):
    title = models.CharField(max_length=100)
    def __unicode__(self):
        return self.title

class Article(models.Model):
    title = models.CharField(max_length=500)
    abstract = models.CharField(max_length=10000, null=True)
    pmid = models.IntegerField()
    terms = models.ManyToManyField('MeshTerm', null=True)
    substances = models.ManyToManyField('Substance', null=True)
    journal = models.ForeignKey('Journal', null=True)
    full_text_link = models.CharField(max_length=1000, null=True)
    authors = models.ManyToManyField('Author', null=True)
    pub_year = models.IntegerField(null=True)
    #suggester = models.ForeignKey('User', null=True)
    author_list_str = models.CharField(max_length=500, null=True)
    
    def __unicode__(self):
        return self.title.encode("iso-8859-15", "replace")

    def get_data_tables(self):
        return self.datasource.data_table.objects.all()
    def get_full_text(self):
        if self.articlefulltext_set.all().count() > 0:
            return self.articlefulltext_set.all()[0]
        else:
            return None
    def get_full_text_stat(self):
        if self.get_full_text():
            if self.get_full_text().articlefulltextstat_set.all().count() > 0:
                return self.get_full_text().articlefulltextstat_set.all()[0]
            else:
                return None
    def get_publisher(self):
        if self.journal:
            if self.journal.publisher:
                return self.journal.publisher.title
            else: 
                return None
        else:
            return None
    def get_neuron_article_maps(self):
        return self.neuron_concept_map_set.all()

def get_articles_with_ephys_data(validated_only = False):
    if validated_only is True:
        num_min_validated = 1
    else:
        num_min_validated = 0
    articles = Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = num_min_validated,
                                        datatable__datasource__neuronephysdatamap__isnull = False) | 
                                        Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = num_min_validated,
                                          usersubmission__datasource__neuronephysdatamap__isnull = False)).distinct()
    return articles
        
class Author(models.Model):
    first = models.CharField(max_length=100, null=True)
    middle = models.CharField(max_length=100, null=True)
    last = models.CharField(max_length=100, null=True)
    initials = models.CharField(max_length=10, null=True)
    
    def __unicode__(self):
        return u'%s %s' % (self.last, self.initials)

class ArticleFullText(models.Model):
    article = models.ForeignKey('Article')
    full_text_file = models.FileField(upload_to ='full_texts', null=True)
    
    def get_content(self):
        try:
            f = self.full_text_file
            f.open(mode='rb')
            read_lines = f.readlines()
            f.close()
            return ''.join(read_lines)
        except ValueError:
            return ''

class ArticleFullTextStat(models.Model):
    article_full_text = models.ForeignKey('ArticleFullText')
    metadata_processed = models.BooleanField(default = False)
    metadata_human_assigned = models.BooleanField(default = False)
    neuron_article_map_processed = models.BooleanField(default = False)
    data_table_ephys_processed = models.BooleanField(default = False)
    num_unique_ephys_concept_maps = models.IntegerField(null=True)
    methods_tag_found = models.BooleanField(default = False)
    date_mod = models.DateTimeField(blank = False, auto_now = True)

class MeshTerm(models.Model):
    term = models.CharField(max_length=300)

    def __unicode__(self):
        return self.term   
        
class Substance(models.Model):
    term = models.CharField(max_length=300)

    def __unicode__(self):
        return self.term            

class Species(models.Model):
    name = models.CharField(max_length=500)
    
    def __unicode__(self):
        return self.name    

class DataChunk(models.Model):
    class Meta:
        abstract = True
    date_mod = models.DateTimeField(blank = False, auto_now = True)

# A data entity coming from a table in a paper.      
class DataTable(DataChunk):
    link = models.CharField(max_length=1000, null = True)
    table_html = PickledObjectField(null = True)
    table_text = models.CharField(max_length=10000, null = True)
    article = models.ForeignKey('Article')
    needs_expert = models.BooleanField(default = False)
    note = models.CharField(max_length=500, null = True) # human user can add note to further define
    
    def __unicode__(self):
        return u'%s' % self.table_text    

# A data entity coming from a user-uploaded file.      
class UserUpload(DataChunk):
    user = models.ForeignKey('User') # Who uploaded it?  
    path = models.FilePathField() # Where the raw upload is stored on disk.  
    data = PickledObjectField(null = True) # The parsed data.  
    
# A data entity coming from a user-submitted form.      
class UserSubmission(DataChunk):
    user = models.ForeignKey('User') # Who uploaded it?  
    data = PickledObjectField(null = True) # The parsed data.  
    article = models.ForeignKey('Article', null = True)

# user_upload not currently utilized
# data_table stores values datamined from an article's data tables
# user_submission stores any data that does not come from an article's data table 
# user_submission and data_table field are mutually exclusive 
class DataSource(models.Model):
    user_submission = models.ForeignKey('UserSubmission', null = True)
    user_upload = models.ForeignKey('UserUpload', null = True)
    data_table = models.ForeignKey('DataTable', null = True)
    
class MetaData(models.Model):
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=100, null = True) # captures nominal metadata (eg species)
    cont_value = models.ForeignKey('ContValue', null = True) # captures continuous metadata (eg age) 
    ref_text = models.ForeignKey('ReferenceText', null = True) # captures text from which this metadata entry was mined
    #added_by = models.ForeignKey('User', null = True)
    #times_validated = models.IntegerField(default = 0)
    #note = models.CharField(max_length=200, null = True)  
    def __unicode__(self):
        if self.value:
            return u'%s : %s' % (self.name, self.value)
        else:
            return u'%s : %.1f' % (self.name, self.cont_value.mean)
            # return u'%s' % (self.name)
            
class ReferenceText(models.Model):
    text = models.CharField(max_length=3000)

class ContValue(models.Model):
    mean = models.FloatField() # mean is always computed, even if not explicitly stated
    stdev = models.FloatField(null = True)
    stderr = models.FloatField(null = True)
    min_range = models.FloatField(null = True)
    max_range = models.FloatField(null = True)
    n = models.IntegerField(null = True)
    def __unicode__(self):
        if self.min_range and self.max_range:
            return u'%.1f - %.1f' % (self.min_range, self.max_range)
        elif self.stderr and self.mean:
            return u'%.1f \xb1 %.1f' % (self.mean, self.stderr)
        else:
            return u'%s' % (self.mean)

class ArticleMetaDataMap(models.Model):
    article = models.ForeignKey('Article') 
    metadata = models.ForeignKey('MetaData') 
    date_mod = models.DateTimeField(blank = False, auto_now = True)
    added_by = models.ForeignKey('User', null = True)
    times_validated = models.IntegerField(default = 0, null = True)
    note = models.CharField(max_length=200, null = True) # human user can add note to further define
    validated_by = models.ManyToManyField('UserValidation', null=True)
    def __unicode__(self):
        return u'%s, %s' % (self.article, self.metadata)

class UserValidation(models.Model):
    date_mod = models.DateTimeField(blank = False, auto_now = True)
    user = models.ForeignKey('User')

class ConceptMap(models.Model):
    class Meta:
        abstract = True    
    source = models.ForeignKey('DataSource')
    ref_text = models.CharField(max_length=200, null = True)
    match_quality = models.IntegerField(null = True)
    dt_id = models.CharField(max_length=20, null = True)
    date_mod = models.DateTimeField(blank = False, auto_now = True)
    added_by = models.ForeignKey('User', null = True) # user who first added the concept map
    validated_by = models.ManyToManyField('UserValidation', null=True)
    times_validated = models.IntegerField(default = 0)
    note = models.CharField(max_length=200, null = True) # this is a curation note

    def get_article(self):
        article = self.source.data_table.article
        return article
    
class EphysConceptMap(ConceptMap):
    ephys_prop = models.ForeignKey('EphysProp')
    
    def __unicode__(self):
        return u'%s %s' % (self.ref_text.encode("iso-8859-15", "replace"), self.ephys_prop.name)    

class NeuronConceptMap(ConceptMap):
    neuron = models.ForeignKey('Neuron')
    
    # add free text field here?
    def __unicode__(self):
        try:
            return u'%s %s' % (self.ref_text.encode("iso-8859-15", "replace"), self.neuron.name)    
        except:
            return u'No neuron syn found'

class NeuronEphysDataMap(ConceptMap):
    neuron_concept_map = models.ForeignKey('NeuronConceptMap')
    ephys_concept_map = models.ForeignKey('EphysConceptMap')
    val = models.FloatField()
    err = models.FloatField(null = True)
    n = models.IntegerField(null = True)
    val_norm = models.FloatField(null = True) # Used to convert 'val' to the unit natural to the corresponding ephys prop.  
    metadata = models.ManyToManyField('MetaData')
    norm_flag = models.BooleanField(default = False) # used to indicate whether data has been checked for correct normalization
    def __unicode__(self):
        return u'Neuron: %s \n Ephys: %s \n Value: %.1f' % (self.neuron_concept_map, self.ephys_concept_map, self.val)

class Unit(models.Model):
    name = models.CharField(max_length=20,choices=(('A','Amps'),('V','Volts'),('Ohms',u'\u03A9'),('F','Farads'),('s','Seconds'),('Hz','Hertz'),('m', 'Meters'),('ratio', 'Ratio')))
    prefix = models.CharField(max_length=1,choices=(('f','f'),('p','p'),('u',u'\u03BC'),('m','m'),('',''),('k','k'),('M','M'),('G','G'),('T','T')))
    def __unicode__(self):
        return u'%s%s' % (self.prefix,self.name)                
        
class NeuronArticleMap(models.Model):
    neuron = models.ForeignKey('Neuron')
    num_mentions = models.IntegerField(null=True)
    article = models.ForeignKey('Article', null = True)
    date_mod = models.DateTimeField(blank = False, auto_now = True)
    added_by = models.ForeignKey('User', null = True)
    def __unicode__(self):
        x = self.num_mentions if self.num_mentions is not None else 0
        return u'Neuron name: %s \n Num Mentions: %d \n Title: %s' % \
                (self.neuron.name, x, self.article.title)
    
class Summary(models.Model):
    class Meta:
        abstract = True
    num_nedms = models.IntegerField(null = True) # What is this?  
    date_mod = models.DateTimeField(auto_now = True)    
    data = models.TextField(default='')
    
class ArticleSummary(Summary):
    article = models.ForeignKey('Article')
    num_neurons = models.IntegerField(null = True)

class PropSummary(Summary):
    class Meta:
        abstract = True
    num_articles = models.IntegerField(null = True)
    
class NeuronSummary(PropSummary):
    neuron = models.ForeignKey('Neuron')
    num_ephysprops = models.IntegerField(null = True)
    # Possibly move the following into data field.  
    cluster_xval = models.FloatField(null = True)
    cluster_yval = models.FloatField(null = True)
    
class EphysPropSummary(PropSummary):
    ephys_prop = models.ForeignKey('EphysProp')
    num_neurons = models.IntegerField(null = True)
    # Possibly move the following into data field.  
    value_mean_neurons = models.FloatField(null = True)
    value_mean_articles = models.FloatField(null = True)
    value_sd_neurons = models.FloatField(null = True)
    value_sd_articles = models.FloatField(null = True)
    
class NeuronEphysSummary(PropSummary):
    ephys_prop = models.ForeignKey('EphysProp')
    neuron = models.ForeignKey('Neuron')
    # Possibly move the following into data field.  
    value_mean = models.FloatField(null = True)
    value_sd = models.FloatField(null = True)

# This model does not store any data in the database - it serves only as a template for neuron_data_add view
class NeuronDataAddMain(models.Model):
    pubmed_id = models.CharField(max_length=255)

# This model does not store any data in the database - it serves only as a template for neuron_data_add view    
class NeuronData(models.Model):
    article_id = models.ForeignKey(NeuronDataAddMain)
    neuron_name = models.CharField(max_length=255)
    
# This model does not store any data in the database - it serves only as a template for neuron_data_add view
class EphysProperty(models.Model):
    neuron_id = models.ForeignKey(NeuronData)
    ephys_name = models.CharField(max_length=255)
    ephys_value = models.CharField(max_length=255)