from allauth.account import views
from django.shortcuts import redirect

class LoginView(views.LoginView):
    template_name = 'accounts/registration/login.html'

    def dispatch(self, request, *args, **kwargs):
        response = super(LoginView, self).dispatch(request, *args, **kwargs)
        return response

    def form_valid(self, form):
      return super(LoginView, self).form_valid(form)

class SignupView(views.SignupView):
    template_name = 'accounts/registration/signup.html'

    def get_context_data(self, **kwargs):
        context = super(SignupView, self).get_context_data(**kwargs)
        return context


class LogoutView(views.LogoutView):

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def post(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            self.logout()
        return redirect('/')

