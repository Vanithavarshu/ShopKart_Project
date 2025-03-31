"""from django.utils.deprecation import MiddlewareMixin

class CustomSessionMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Set the cookie on the response, NOT on request.session
        response.set_cookie("shop_session", "your_session_value", max_age=3600)
        return response"""
