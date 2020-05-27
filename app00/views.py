from django.shortcuts import render
from django.views.generic import TemplateView

class IndexView(TemplateView):
   template_name = 'app00/index.html'

   def get(self, request, **kwargs):
      context = {
         'items': 'TEST'
      }
      return self.render_to_response(context)
