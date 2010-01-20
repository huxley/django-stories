from django import forms
from settings import MARKUP_CHOICES
import datetime
from django.contrib.sites.models import Site

from models import Story

class StoryForm(forms.ModelForm):
    markup = forms.CharField(max_length=3, required=False,
                             widget=forms.Select(choices=MARKUP_CHOICES, 
                             attrs={'onchange':'changeMarkup(this)'}))
    class Meta:
        model = Story
    
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                     initial=None, error_class=forms.util.ErrorList, label_suffix=':',
                     empty_permitted=False, instance=None):
        # Set a default publish time and the current site if it is a new object
        if not instance and (initial is not None and not initial.has_key('publish_date')):
            initial['publish_date'] = datetime.datetime.now().date
        if not instance and (initial is not None and not initial.has_key('site')):
            initial['site'] = Site.objects.get_current().id
        super(StoryForm, self).__init__(data, files, auto_id, prefix, initial, 
                                        error_class, label_suffix, 
                                        empty_permitted, instance)
                                        
    def save(self, **kw):
        # 1 - Get the old stuff before saving
        if self.instance.id is None:
            old_headline = old_body = old_markup = ''
            new = True
        else:
            old_headline = self.instance.headline
            old_body = self.instance.body
            old_markup = self.instance.markup
            new = False

        # 2 - Save the Article
        story = super(StoryForm, self).save(**kw)

        # 3 - Set creator
        # editor = getattr(self, 'editor', None)
        if new:
            # if editor is not None:
            #     article.creator = editor
            #     article.group = group
            story.save()

        # 4 - Create new revision
        if not old_body == story.body:
            changeset = story.new_revision(
                old_body, old_headline, old_markup, None)

        return story#, changeset