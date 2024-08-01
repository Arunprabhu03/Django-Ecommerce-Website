#For preventing a logged in user from accessing the login page again by using the /login url

from django.shortcuts import redirect

def anonymous_required(view_function, redirect_to=None):
    """
    Decorator for views that checks that the user is not logged in.
    """
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if redirect_to is not None:
                return redirect(redirect_to)
            else:
                return redirect('home')  # Redirect to home or another appropriate URL
        else:
            return view_function(request, *args, **kwargs)
    return wrapped_view
