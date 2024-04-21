import threading

class AckTracker:
    def __init__(self, start_seq=0):
        self.current_seq = start_seq
        self.pending_acks = set()
        self.lock = threading.Lock()

    def get_next_sequence_number(self):
        with self.lock:
            self.current_seq += 1
            return self.current_seq

    def add_request(self):
        seq_num = self.get_next_sequence_number()
        with self.lock:
            self.pending_acks.add(seq_num)   
        return seq_num

    def remove_ack(self, seq_num):
        with self.lock:
            if seq_num in self.pending_acks:
                self.pending_acks.discard(seq_num)
                

    def __str__(self):
        with self.lock:
            return str(self.pending_acks)

# Initialize AckTracker instance
ack_list = AckTracker()