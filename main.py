import Frontend
import Backend

from multiprocessing import Process, Pipe

if __name__ == "__main__":
    frontend_conn, backend_conn = Pipe()
    pFrontend = Process(target=Frontend.thread_init, args=(frontend_conn,))
    pFrontend.start()

    backendInstance = Backend.ExecutionController()
    pBackend = Process(target=backendInstance.main, args=(backend_conn,))
    pBackend.start()