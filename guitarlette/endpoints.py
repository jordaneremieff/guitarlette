from starlette.endpoints import HTTPEndpoint
from starlette.responses import HTMLResponse


class TemplateEndpoint(HTTPEndpoint):

    template_name = None
    response_class = HTMLResponse

    async def get_context(self, request):
        context = {"request": request}
        return context

    async def get(self, request):
        template = self.scope["app"].get_template(self.template_name)
        context = await self.get_context(request)
        content = template.render(**context)
        return self.response_class(content)
