from .models import SMBResource
from smb.SMBConnection import SMBConnection
import socket
from threading import Lock
import tempfile


class SMBInterface:
    def __init__(self):
        self.conns = []
        self.client_machine_name = "Racine"
        self.lock = Lock()

    def get_file(self, path):
        """Creates a temporary file object and reads the content of a remote SMB file into it.

        Parameters
        ----------
        path : str
            The path pointing to the SMB resource and location within the resource.

        Returns
        -------
        file : file object
            A file object.
        """

        # process the path and check if requested resource exists
        resource, path_on_server = self.process_smb_path(path)
        if not resource:
            return None

        # establish connection or use existing one
        conn = self._get_connection(resource)
        if not conn:
            return None

        # retrieve the requested file from the resource
        file_obj = tempfile.NamedTemporaryFile()
        try:
            file_attributes, filesize = conn.retrieveFile(
                resource.sharename, path_on_server, file_obj
            )
            file_obj.seek(0)  # go back to the beginning
        except Exception:  # if we have any problem retrieving the file
            # TODO: specify exception
            self._free_connection(conn)
            return None

        self._free_connection(conn)
        return file_obj

    def list_path(self, path):
        # TODO: doc string

        # process the path and check if requested resource exists
        resource, path_on_server = self.process_smb_path(path)
        if not resource:
            return None

        # establish connection or use existing one
        conn = self._get_connection(resource)
        if not conn:
            return None

        # TODO: error handling
        list_path = conn.listPath(resource.sharename, path_on_server)

        self._free_connection(conn)

        return list_path

    def process_smb_path(self, path):
        """Splits up the SMB path of type "/ResourceName/path_in_resource".

        The path in the resource is not necessarily the same as the path on the server, because
        a resource can already point to a subdirectory on the server. If the path is empty,
        this function will return None, ''. The same will be returned if the requested resource
        does not exist.

        Parameters
        ----------
        path: str

        Returns
        -------
        resource : SMBResource
        path_on_server : str
        """

        # we want to be as tolerant as possible and accept paths like
        # "/ResourceName/path_in_resource", but also
        # "ResourceName/path_in_resource" or "" or "/"
        toks = path.strip("/").split("/")

        # check if we have at least a resource name
        if len(toks) == 0:
            return None, ""  # no resource name given

        resource = SMBResource.query.filter_by(name=toks[0]).first()
        if resource is None:  # resource not found in database
            return None, ""

        path_in_resource = "" if len(toks) == 1 else "/".join(toks[1:])

        # make sure the path is constructed correctly even if resource.path
        # or path_in_resource are empty or None
        path_on_server = "/".join(filter(None, [resource.path.strip("/"), path_in_resource]))

        return resource, path_on_server

    def _get_connection(self, resource):
        # TODO: doc string
        conn = None

        with self.lock:
            for c in self.conns:
                # use resource name as key, not resource itself (in case database session expires,
                # weird stuff might happen otherwise)
                if c.resource == resource.name and not c.inuse:
                    c.inuse = True
                    conn = c
                    break

        # TODO: define a max number of connections to be established

        # if there is already a connection, we check if it's still working
        need_new_conn = True
        if conn is not None:
            try:
                echo = conn.echo("0", timeout=1)  # 1 second timeout
                if echo == "0":
                    return conn
                else:
                    self.conns.remove(conn)
            except Exception:
                self.conns.remove(conn)

        if need_new_conn:
            conn = self._new_connection(resource)
            if conn:
                conn.resource = resource.name
                conn.inuse = True
                self.conns.append(conn)
                return conn

    def _free_connection(self, conn):
        # TODO: doc string
        conn.inuse = False

    def _new_connection(self, resource):
        # TODO: doc string
        # set up SMB connection
        try:
            server_ip = socket.gethostbyname(resource.serveraddr)
        except Exception:  # if host unknown
            return None
        # need to convert unicode -> string apparently...
        conn = SMBConnection(
            str(resource.userid),
            str(resource.password),
            self.client_machine_name,
            str(resource.servername),
            domain=str(resource.domainname),
            use_ntlm_v2=True,
        )
        try:
            # try to connect with a 1 second timeout
            connected = conn.connect(server_ip, port=resource.serverport, timeout=1)
        except Exception:
            connected = False

        return conn if connected else None
