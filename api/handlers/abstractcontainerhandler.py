from bson import ObjectId
from webapp2 import Request

from ..dao.containerutil import container_search
from ..web import base
from ..web.errors import APINotFoundException


class AbstractContainerHandler(base.RequestHandler):
    """
    Asbtract handler that removes the need to know a container's noun before performing an action.
    """

    # pylint: disable=unused-argument
    def handle(self, cid, extra):
        """
        Dispatch a request from /containers/x/... to its proper destination.
        For example:
            /containers/x/files --> x is a project ID --> /projects/x/files
        """

        if ObjectId.is_valid(cid):
            cid = ObjectId(cid)

        results = container_search({'_id': cid}, projection={'_id': 1})
        if not results:
            raise APINotFoundException('No container {} found'.format(cid))

        # Create new request instance using destination URI (eg. replace containers with cont_name)
        cont_name, _ = results[0]
        destination_environ = self.request.environ
        for key in 'PATH_INFO', 'REQUEST_URI':
            destination_environ[key] = destination_environ[key].replace('containers', cont_name, 1)
        destination_request = Request(destination_environ)

        # Apply SciTranRequest attrs
        destination_request.id = self.request.id
        destination_request.logger = self.request.logger

        # Dispatch the destination request
        self.app.router.dispatch(destination_request, self.response)
