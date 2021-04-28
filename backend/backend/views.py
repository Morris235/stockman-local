# from django.views.generic import View
# from django.http import HttpResponse
# from django.conf import settings
# import os
#
# class ReactAppView(View):
#     def get(self, request):
#         try:
#             FRONT_DIR = 'C:\\Pyvenv\\projects\\site\\stockman\\frontend'
#             with open(os.path.join(FRONT_DIR, 'src', 'index.html')) as file:
#                 return HttpResponse(file.read())
#         except:
#             return HttpResponse(
#                 """
#                 index.html not found! build react app
#                 """,
#                 status=501,
#             )
