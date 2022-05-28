'''
#############################################################################################
@brief Main file to start processes
#############################################################################################
'''

import Frontend
import Backend

from multiprocessing import Process, Pipe

if __name__ == "__main__":
    frontend_conn, backend_conn = Pipe()
    #Frontend.thread_init(backend_conn)
    pFrontend = Process(target=Frontend.thread_init, args=(frontend_conn,))
    pFrontend.start()

    backendInstance = Backend.ExecutionController()
    #backendInstance.main(backend_conn)
    pBackend = Process(target=backendInstance.main, args=(backend_conn,))
    pBackend.start()