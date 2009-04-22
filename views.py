from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse, HttpResponseNotModified, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError
from django import forms
from django.template import RequestContext
from django.contrib.sites.models import Site

from dimension.models import FieldType, Category

import gdata.auth
import gdata.analytics.service

import csv

try:
    import cPickle as pickle
except:
    import pickle


from gdata_service import DjangoGoogleAnalyticsService

def redirect_google_analytics(request, next='/successful_connect_google_analytics'):
    """
    send a user to google 
    """
    next = '/' + next.lstrip('/')
    callback_url = 'http://%s%s' % (Site.objects.get_current().domain, next)
    g = DjangoGoogleAnalyticsService()
    g.callback_url = callback_url
    g.request_token()
    request.session.set_expiry(86000)
    request.session['ga_controller'] = pickle.dumps(g)
    return HttpResponseRedirect(g.authorization_url())
    
def successful_connect_google_analytics(request):
    """
    catch the response from Google, and finish authenticating the user
    """
    if request.method == 'GET':
        if 'oauth_token' in request.GET:
            if 'ga_controller' not in request.session:
                return HttpResponseRedirect('/redirect_google_analytics/')
            g = pickle.loads(request.session['ga_controller'])
            access_token = g.upgrade_token()
            request.session['ga_controller'] = pickle.dumps(g)
            if access_token:
                return HttpResponseRedirect('/api_call/') #, access_token=access_token, scopes=scopes)
            else:
                return HttpResponseBadRequest("Bad oauth token")
        else:
            return HttpResponseBadRequest("No oauth token in callback: this callback function is only for returning from google")
    else:
        return HttpResponseBadRequest("Why we posting here?")

class DimensionSelectForm(forms.Form):
    """
    Form for selecting dimensions, filters and metrics
    """
    profiles = forms.ChoiceField(help_text="Choose the profile you wish to use.")
    
    dimensions = forms.ModelMultipleChoiceField(help_text="Use Ctrl or the Apple button to select multiple entries",
                                   queryset=FieldType.objects.filter(category__in=Category.objects.filter(subdivision='dimension')).order_by("name"))
    metrics = forms.ModelMultipleChoiceField(help_text="Use Ctrl or the Apple button to select multiple entries",
                                queryset=FieldType.objects.filter(category__in=Category.objects.filter(subdivision='metric')).order_by("name"))
    sort = forms.ModelChoiceField( #help_text="Choose the sort metric",
                                queryset=FieldType.objects.all().order_by("name"),
                                required=False)
    filter = forms.ModelChoiceField( #help_text="Choose the filter you wish to apply",
                                        queryset=FieldType.objects.all().order_by("name"),
                                        required=False)
    filter_value = forms.CharField( help_text="Currently, all filters are limited to the == equality parameter",
                                   required=False)
    filter_2 = forms.ModelChoiceField( #help_text="Choose the filter you wish to apply",
                                        queryset=FieldType.objects.all().order_by("name"),
                                        required=False)
    filter_2_value = forms.CharField( #help_text="Currently, only "
                                     required=False)
    filter_3 = forms.ModelChoiceField( #help_text="Choose the filter you wish to apply",
                                        queryset=FieldType.objects.all().order_by("name"),
                                        required=False)
    filter_3_value = forms.CharField( #help_text="If you selected a filter, select a value to filter by",
                                     required=False)
    start_date = forms.DateField(widget=forms.TextInput(attrs={ 'class': 'field text medium date-pick', 'required': True }),
                           label=(u'Start date'), help_text="MM/DD/YYYY.")
    end_date = forms.DateField(widget=forms.TextInput(attrs={ 'class': 'field text medium date-pick', 'required': True }),
                                label=(u'End date'), help_text="MM/DD/YYYY.")
                   
    def __init__(self, account_list, *args, **kwargs):
        super(DimensionSelectForm, self).__init__(*args, **kwargs)
        self.fields['profiles'].choices = [(entry.profileId.value, 
                                            entry.title.text) for entry in account_list]
        self.name_lookup = dict([(entry.profileId.value, entry.title.text) for entry in account_list])
                                
    def clean(self):
        
        sort = self.cleaned_data.get("sort")
        
        #Add the sort dimension/metric if it is not already part of the list
        if sort and sort.category.subdivision == 'dimension':
            if sort not in self.cleaned_data.get("dimensions"):
                self.cleaned_data.get("dimensions").append(sort)
        elif sort and sort.category.subdivision == 'metric':
            if sort not in self.cleaned_data.get("metrics"):
                self.cleaned_data.get("metrics").append(sort)
        
        dimensions = self.cleaned_data.get("dimensions", [])[:]
        metrics = self.cleaned_data.get("metrics", [])[:]
        filters = dict([(self.cleaned_data.get("filter"), self.cleaned_data.get("filter_value")),
                       (self.cleaned_data.get("filter_2"), self.cleaned_data.get("filter_2_value")),
                       (self.cleaned_data.get("filter_3"), self.cleaned_data.get("filter_3_value"))])
                       
        match_errors = []
        
        while dimensions:
            d1 = dimensions.pop()
            for d2 in dimensions:
                if not d1.compatable_with(d2):
                    match_errors += ["Dimension %s is not compatible with dimension %s." % (d1, d2)]
                    
            for m2 in metrics:
                if not d1.compatable_with(m2):
                    match_errors += ["Dimension %s is not compatible with metric %s." % (d1, m2)]
                    
            for f2_key, f2_value in filters.iteritems():
                if f2_value and not d1.compatable_with(f2_key):
                    match_errors += ["Dimension %s is not compatible with filter %s." % (d1, f2_key)]
                    
        while metrics:
            m1 = metrics.pop()
            for m2 in metrics:
                if not m1.compatable_with(m2):
                    match_errors += ["Metric %s is not compatible with metric %s." % (m1, m2)]
                    
            for f2_key, f2_value in filters.iteritems():
                if f2_value and not d1.compatable_with(f2_key):
                    match_errors += ["Dimension %s is not compatible with filter %s." % (d1, f2_key)]
        
         
        while filters:
            f1_key, f1_value = filters.popitem()
            if not f1_value:
                continue
            for f2_key, f2_value in filters.iteritems():
                if f2_value and f1_key.compatable_with(f2_key):
                    match_errors += ["Filter %s is not compatible with filter %s." % (f1_key, f2_key)]
            
        if match_errors:
            raise forms.ValidationError('<br>\n'.join(match_errors))
                    
        return self.cleaned_data
        
    def clean_name(self):
        return self.cleaned_data.get('name', False) or self.name_lookup.get(self.cleaned_data.get('profiles', 0),'Default')
                    
def api_call(request):
    if 'ga_controller' not in request.session or not pickle.loads(request.session['ga_controller']).token_upgraded:
        return HttpResponseRedirect('/redirect_google_analytics/')
    
    if request.method == 'POST':
        form = DimensionSelectForm(request.session.get('ga_account_list', 
                                                       pickle.loads(request.session['ga_controller']).GetAccountList('default').entry), 
                                                       request.POST)
        if form.is_valid():
            #save all the form values to the session
            
            filters = dict([(form.cleaned_data.get("filter"), form.cleaned_data.get("filter_value")),
                           (form.cleaned_data.get("filter_2"), form.cleaned_data.get("filter_2_value")),
                           (form.cleaned_data.get("filter_3"), form.cleaned_data.get("filter_3_value"))])
            
            request.session['ga_parameters'] = form.cleaned_data
            
            #Do the API call
            g = pickle.loads(request.session['ga_controller'])
            
            feed = g.GetData(ids='ga:%s' % form.cleaned_data['profiles'], 
                                dimensions=','.join(['%s' % d.name for d in form.cleaned_data['dimensions']]),
                                metrics=','.join(['%s' % m.name for m in form.cleaned_data['metrics']]),
                                sort='-%s' % (form.cleaned_data.get("sort", None) or form.cleaned_data['metrics'][0]).name,
                                filters=','.join(['%s==%s' % (key, value) for key, value in filters.iteritems() if value]),
                                start_date=form.cleaned_data['start_date'].strftime('%Y-%m-%d'),
                                end_date=form.cleaned_data['end_date'].strftime('%Y-%m-%d'),
                                start_index=1, max_results=11)
                                
            parameters = [('ids', 'ga:%s' % form.cleaned_data['profiles']), 
                            ('dimensions', ','.join(['%s' % d.name for d in form.cleaned_data['dimensions']])),
                            ('metrics', ','.join(['%s' % m.name for m in form.cleaned_data['metrics']])),
                            ('sort', '-%s' % (form.cleaned_data.get("sort", None) or form.cleaned_data['metrics'][0]).name,),
                            ('filters', ','.join(['%s==%s' % (key, value) for key, value in filters.iteritems() if value])),
                            ('start_date', form.cleaned_data['start_date'].strftime('%Y-%m-%d')),
                            ('end_date', form.cleaned_data['end_date'].strftime('%Y-%m-%d')),]
                                
            parameter_names = [dim.name for dim in feed.entry[0].dimension] + [met.name for met in feed.entry[0].metric]
            
            entry_values = [[dim.value for dim in entry.dimension] + [met.value for met in entry.metric] for entry in feed.entry]
            
            #Kill the not set entry for the summary if it exists
            new_entry_values = []
            for ent in entry_values:
                if "(not set)" not in ent:
                    new_entry_values.append(ent)
                    
            entry_values = new_entry_values[:10]
            
            
            return render_to_response('summary.html',
                                      {
                                      'parameter_names': parameter_names,
                                      'entry_values': entry_values or [["There is no data for these parameters."]],
                                      'parameters': parameters,
                                      })
            
        
    else:
        
        feed = pickle.loads(request.session['ga_controller']).GetAccountList('default')
        request.session['ga_account_list'] = feed.entry
        form = DimensionSelectForm(feed.entry)
        
    return render_to_response('explorer_form.html', 
                              {
                                'next': '/api_call/',
                                'form': form,
                                'title': 'Choose your API parameters',
                                'messages': ['You can pick anything you want'],
                              },
                               context_instance=RequestContext(request))
                               
                               
def download_file(request):
    
    if 'ga_controller' not in request.session or not pickle.loads(request.session['ga_controller']).token_upgraded:
        return HttpResponseRedirect('/redirect_google_analytics/')
    
    g = pickle.loads(request.session['ga_controller'])
    parameters = request.session['ga_parameters']
    
    filters = dict([(parameters.get("filter"), parameters.get("filter_value")),
                   (parameters.get("filter_2"), parameters.get("filter_2_value")),
                   (parameters.get("filter_3"), parameters.get("filter_3_value"))])
    
    feed = g.GetData(ids='ga:%s' % parameters['profiles'], 
                        dimensions=','.join(['%s' % d.name for d in parameters['dimensions']]),
                        metrics=','.join(['%s' % m.name for m in parameters['metrics']]),
                        sort='-%s' % (parameters['sort'] or parameters['metrics'][0]).name,
                        filters=','.join(['%s==%s' % (key, value) for key, value in filters.iteritems() if value]),
                        start_date=parameters['start_date'].strftime('%Y-%m-%d'),
                        end_date=parameters['end_date'].strftime('%Y-%m-%d'),
                        start_index=1)

    total_results = feed.total_results.text

    i = 1000
    while i < min(10000, total_results):
        additional_feed = g.GetData(ids='ga:%s' % parameters['profiles'], 
                                    dimensions=','.join(['%s' % d.name for d in parameters['dimensions']]),
                                    metrics=','.join(['%s' % m.name for m in parameters['metrics']]),
                                    sort='-%s' % (parameters['sort'] or parameters['metrics']).name,
                                    filters=','.join(['%s==%s' % (key, value) for key, value in filters.iteritems() if value]),
                                    start_date=parameters['start_date'].strftime('%Y-%m-%d'),
                                    end_date=parameters['end_date'].strftime('%Y-%m-%d'),
                                    start_index=i+1)

        feed.entry += additional_feed.entry

        i += 1000
        
    parameter_names = [dim.name for dim in feed.entry[0].dimension] + [met.name for met in feed.entry[0].metric]
        
    # output_string = '\t'.join(parameter_names) + '\n'
    # for entry in feed.entry:
    #     output_string += '\t'.join([dim.value for dim in entry.dimension] + [met.value for met in entry.metric]) + '\n'
        
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=google_api_data.csv'
    
    writer = csv.writer(response)
    writer.writerow(parameter_names)
    for entry in feed.entry:
        writer.writerow([dim.value for dim in entry.dimension] + [met.value for met in entry.metric])
        
    return response
    
def download_code(request):
    """
    Download a working copy of the code from a template
    """
    if 'ga_parameters' not in request.session:
        return HttpResponseRedirect('/api_call/')
    
    parameters = request.session['ga_parameters']
    
    filters = dict([(parameters.get("filter"), parameters.get("filter_value")),
                   (parameters.get("filter_2"), parameters.get("filter_2_value")),
                   (parameters.get("filter_3"), parameters.get("filter_3_value"))])
                   
    ids = 'ga:%s' % parameters['profiles']
    dimensions = ','.join(['%s' % d.name for d in parameters['dimensions']])
    metrics = ','.join(['%s' % m.name for m in parameters['metrics']])
    sort = '-%s' % (parameters['sort'] or parameters['metrics']).name
    filters = ','.join(['%s==%s' % (key, value) for key, value in filters.iteritems() if value])
    start_date = parameters['start_date'].strftime('%Y-%m-%d')
    end_date = parameters['end_date'].strftime('%Y-%m-%d')
    
    dimension_list = [dim.name.replace('ga:', '') for dim in parameters['dimensions']]
    metric_list = [met.name.replace('ga:', '') for met in parameters['metrics']]
    
    return render_to_response('auto_generated_code.py',
                              {
                              'ids': ids,
                              'dimensions': dimensions,
                              'metrics': metrics,
                              'sort': sort,
                              'filters': filters,
                              'start_date': start_date,
                              'end_date': end_date,
                              'dimension_list': dimension_list,
                              'metric_list': metric_list,
                              },
                               mimetype='text/plain',
                               context_instance=RequestContext(request))