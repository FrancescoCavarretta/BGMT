


class Pool:
    def __init__(self):
        from mpi4py import MPI
        import sys

       	if MPI.COMM_WORLD.Get_rank() > 0:
            self.__map__consumer()
            sys.exit(0)


    def map(self, func, args):
        from mpi4py import MPI
        import sys
        
        if MPI.COMM_WORLD.Get_rank() == 0:
            return self.__map_producer(func, args)
        else:
            self.__map__consumer()
            sys.exit(0)

    def __map_producer(self, func, args):
        from mpi4py import MPI
        mpi_comm = MPI.COMM_WORLD
        
        # return
        ret_message = []

        # consumer available for running simulations
        free_ranks = list(range(1, mpi_comm.Get_size()))

        while len(args):
            # occupy all the ranks
            while len(free_ranks) and len(args):
                # get parameters, assemble message and submit
                mpi_comm.send(obj  ={'args':args.pop(), 'function':func},
                              dest =free_ranks.pop(),
                              tag  =0)
                
            # receive the message
            message = mpi_comm.recv()
            ret_message.append(message['output'])
            free_ranks.append(message['rank'])

        # processes left
        while len(free_ranks) < mpi_comm.Get_size() - 1:
            # receive the message
            message = mpi_comm.recv()
            ret_message.append(message['output'])
            free_ranks.append(message['rank'])

        # send termination signal to all
        for rank in range(1, mpi_comm.Get_size()):
            mpi_comm.send(obj  =None,
                          dest =rank,
                          tag  =0)

        return ret_message



    def __map__consumer(self):
        from mpi4py import MPI
        mpi_comm = MPI.COMM_WORLD

        rank = mpi_comm.Get_rank()

        # receive a message
        message = mpi_comm.recv(source =0,
                                tag    =0)

        while message:
            # unpack info
            func = message['function']
            args = message['args']

            # run function
            output = func(*args)

            # send out
            mpi_comm.send(obj  =dict(output=output, rank=rank),
                          dest =0,
                          tag  =0)
            
            # receive a message
            message = mpi_comm.recv(source =0,
                                    tag    =0)
    

