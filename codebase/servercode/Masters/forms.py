from django import forms
from .models import City,Survey
import urllib2,urllib
import json
import simplejson 
from django.conf import settings

survey_list=[]

class SurveyCreateForm(forms.ModelForm): 
    kobotoolSurvey_id = forms.ChoiceField(widget=forms.Select(),required=True)
    kobotoolSurvey_url = forms.CharField(required=True)    
    def __init__(self,*args,**kwargs):
        super(SurveyCreateForm,self).__init__(*args,**kwargs)
        self.list_i=[]
        self.list_i=getKoboIdList()   
        self.fields['kobotoolSurvey_id'].choices=self.list_i
        self.fields['kobotoolSurvey_id'].initial=[0]
        self.fields['kobotoolSurvey_url'].required = False 
        #self.fields['kobotoolSurvey_url'].widget.attrs['readonly'] = True 
    class Meta:
        model=Survey
        fields = ['Name','Description','City_id','Survey_type','AnalysisThreshold','kobotoolSurvey_id']
    
    def save(self, *args, **kwargs):
        instance = super(SurveyCreateForm,self).save(commit=False)
        kobourl=""
        data = self.cleaned_data
        print data
        #kobocat ID and Kobocat URL Mapping
        for value in self.list_i:
            for survey_value in survey_list:  
                if survey_value[0]== value[0]:
                    kobourl= survey_value[1]
        
        # Saving Data 
        #=======================================================================
        # survey_data = Survey(Name=data['Name'],Description=data['Description'],City_id=data['City_id'],
        #                      Survey_type=data['Survey_type'],AnalysisThreshold=data['AnalysisThreshold'],
        #                      kobotoolSurvey_id=data['kobotoolSurvey_id'],kobotoolSurvey_url=kobourl)
        #=======================================================================
        
       
        instance.kobotoolSurvey_url=kobourl
        instance.save()
        return instance
        
def getKoboIdList():
    #url="http://kc.shelter-associates.org/api/v1/forms?format=json"   
    url=settings.KOBOCAT_FORM_URL
    req = urllib2.Request(url)
    req.add_header('Authorization', settings.KOBOCAT_TOKEN)
    resp = urllib2.urlopen(req)
    content = resp.read()         
    data = json.loads(content) 
    
    temp_arr=[]
    temp_arr.append(('','-----------'))
    for value in data:  
        #=======================================================================
        # survey_list={}
        # survey_list['id']= value['id_string']
        # survey_list['value']=value['url']
        #=======================================================================
        survey_list.append((value['id_string'],value['url']))  
        temp_arr.append((value['id_string'],value['id_string']))            
      
    return temp_arr        