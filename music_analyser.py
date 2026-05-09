##############################
#   Music Pattern Analyser   #
##############################

from collections import deque

class TrieNode:
    slots = [
        'children',
        'song_count',
        'last_seen_song',
        'pattern_reference',
        'parent',
        'parent_difference'
    ]
    
    def __init__(self):
        """
        Function Description:
            Initializes a TrieNode for storing musical pattern information in the analyser trie.
            Each node represents a musical pattern defined by interval sequences and tracks how many
            distinct songs contain this pattern. The node stores children for all possible interval
            transitions (-25 to +25) and maintains parent references for pattern reconstruction.
            This allows the trie to identify transposition equivalent patterns across different songs.
        
        Attributes:
            - children: Array of 51 possible children nodes for intervals from -25 to +25
            - song_count: Number of distinct songs that contain the pattern ending at this node
            - last_seen_song: Last song index in which this pattern was encountered to avoid duplicate
            - pattern_reference: A representative (song_index, start_position) storing one occurrence 
                                 of this pattern
            - parent: Reference to the parent node in the trie
            - parent_difference: The interval value that leads from parents to this nodes
        
        Time Complexity:
            O(1)
            
        Aux Space Complexity:
            O(1)
        """
        self.children = [None] * 51
        self.song_count = 0
        self.last_seen_song = -1
        self.pattern_reference = None
        self.parent = None
        self.parent_difference = None


class Analyser:
    def __init__(self, sequences):
        """
        Function Description:
            Initializes the Analyser with a list of musical note sequences and constructs an interval-based
            trie data structure for pattern recognition.
            This class enables efficient detection of the most frequent transposition-invariant
            musical patterns across multiple songs, by using interval-based matching that recognizes
            patterns regardless of their musical key.
            
        Approach Description:
            1. I preprocess all musical sequences by converting each character sequence into an integer
               array of note values ranging from 0 ('a') to 25 ('z'). This representation allows me to compute
               pitch intervals numerically. For each song, I also determine the maximum sequence length M among
               all non-empty sequences

            2. I then construct an interval-based trie that stores all possible patterns derived from note
               intervals across all songs. For each song and each possible starting position, I compute the
               interval differences between consecutive notes and insert these interval sequences into the trie.
               Each node in the trie represents a specific interval-based pattern, and its song_count reflects
               how many unique songs contain that pattern.
            
            3. During insertion, I track the last song index in which each pattern appeared using
               last_seen_song to ensure that a pattern is counted only once per song. I also maintain
               pattern_reference, which stores one representative occurrence of that pattern for later 
               reconstruction of the original note sequence.

            4. After building the trie, I perform a breadth-first traversal to identify the most frequent pattern
               for each possible length. For each node visited, I compare its song_count with the current best
               pattern of that length. If it is higher, I update the stored best pattern and reference.

            5. Finally, I store the best pattern node for every valid length in self.best_patterns, enabling
               getFrequentPattern(pattern_length) to reconstruct and return the most frequent transposition-
               invariant pattern in O(K) time, where K is the requested pattern length.
            
        Input:
            - sequences: List of strings where each string is a musical sequence, notes 'a'-'z'
            
        Output:
            - Initialized Analyser object ready for pattern queries by using getFrequentPattern()
            - No direct return values
            
        Time Complexity:
            O(N*M^2) worst case time complexity, where N is number of sequences and 
            M is maximum length of a sequence

        Time Complexity Analysis:
            - Sequence conversion: 
                Each of the N input sequences is converted into an integer array of note values, where each
                note is mapped from a character in O(1) time. This contributes O(N*M) time overall.

            - Trie Construction:
                For each of N songs, the algorithm iterates through all M possible starting positions.
                From each starting position, it extends patterns over up to M subsequent notes,
                performing O(M) operations per start. As a result, inserting all interval-based
                subsequences into the trie requires O(N*M^2) time in total, since each of the M
                starting points may contribute up to M interval insertions in the worst case.
            
            - Best pattern extraction: 
                After the trie is fully built, a breadth-first traversal is used to identify the most
                frequent pattern for each possible pattern length. 
                Since every node in the trie is visited exactly once, the traversal runs in O(N*M) time.
                The trie contains at most O(N*M) nodes, as each starting position can contribute up to M nodes.
                For each node, only O(1) work is required to update the best pattern for its depth, and a 
                constant-time operation is performed to add its child nodes to the traversal queue.
                Therefore, the total complexity of the extraction phase remains O(N*M).
    
            - Combining all these components yields a total worst case time complexity of
                O(N*M) + O(N*M^2) + O(N*M) = O(N*M^2)
    
        Aux Space Complexity:
            O(N*M) worst case auxiliary space complexity, where N is number of sequences and 
            M is maximum length of a sequence

        Aux Space Complexity Analysis:
            - Sequence storage:
                The analyser converts all input sequences into arrays of integer note values.
                Storing all these note arrays requires O(N*M) space in total, as each of the N sequences
                can contain up to M elements.
    
            - Trie structure:
                The trie is built from all interval-based subsequences across every song.
                In the worst case, the trie contains O(N*M) nodes because each new interval
                insertion may create one new node.
                Each node stores:
                    - children array: O(51) = O(1) space
                    -  Constant number of attributes: song_count, last_seen_song, pattern_reference, parent,
                       parent_difference
                Overall, the total trie space is O(N*M).

            - BFS traversal structure:
                The breadth-first search used for identifying the most frequent pattern stores nodes in a 
                queue proportional to the breadth of the trie. In the worst case, the queue contains O(N*M)
                nodes, contributing O(N*M) additional temporary space.

            - Best Pattern Table:
                The analyser stores the best pattern node reference for each possible length in 
                self.best_patterns. This array uses O(M) space.

            - Combining all these components gives a total auxiliary space complexity of
            O(N*M) + O(N*M) + O(N*M) + O(M) = O(N*M)
        """
        N = len(sequences)
        self.songs = [None] * N
        self.N = N
        self.M = 0
        
        # Convert note sequences ('a'–'z') to integer arrays (0–25)
        for idx, sequence in enumerate(sequences):
            if len(sequence) == 0:
                self.songs[idx] = []
                continue
            note_values = [ord(ch) - ord('a') for ch in sequence]
            self.songs[idx] = note_values
            if len(note_values) > self.M:  
                self.M = len(note_values)
        
        # Build the complete interval trie from all songs
        self.root = TrieNode()
        self.build_complete_trie()
        
        # Find the most frequent pattern per length
        self.best_patterns = [None] * (self.M + 1)
        self.extract_best_patterns()

    def build_complete_trie(self):
        """
        Function Description:
            Constructs the complete interval-based trie by inserting all possible patterns derived from
            every song. For each song, the function considers every possible starting position and extends
            patterns as far as possible, creating trie paths that represent interval sequences. 
            Empty sequences are also safely skipped.

        Input:
            - None (uses self.songs and self.N from instance variables)

        Output:
            - None (modifies the trie rooted at self.root with all interval-based subsequences)

        Time Complexity:
            O(N*M^2), where N is the number of songs and M is the maximum length of a song

        Time Complexity Analysis:
            For each of N songs, the algorithm iterates through M possible starting positions.
            From each starting position, it extends patterns through up to M following notes, inserting
            them into the trie. Each insertion involves O(1) node traversal or creation.
            Therefore, total time = O(N*M*M) = O(N*M^2).

        Aux Space Complexity:
            O(1), as the function uses only constant auxiliary memory (loop counters and references), since
            all data structures (songs, trie nodes) are pre-allocated externally.
        """
        for song_idx in range(self.N):
            notes = self.songs[song_idx]
            if len(notes) == 0:
                continue
            # For each possible start position in the song
            for start in range(len(notes)):
                # Insert all interval subsequences starting at this position
                self.insert_patterns_from_start(notes, start, song_idx)

    def insert_patterns_from_start(self, notes, start, song_idx):
        """
        Function Description:
            Inserts all possible interval-based subsequences starting from a given note position within a
            song into the trie. Each node's song_count is incremented only once per song to ensure 
            accurate frequency tracking across different songs. The process begins at the root 
            (representing the empty or single-note pattern) and extends through consecutive notes,
            creating new trie nodes as needed. The last_seen_song mechanism guarantees that each song 
            is counted only once per pattern.

        Input:
            - notes: Integer list of note values for one song (0-25 for 'a-z')
            - start: Starting index of the subsequence
            - song_idx: Index of the current song being processed

        Output:
            - None (modifies the trie structure by inserting all subsequences beginning at the given
              start position)

        Time Complexity:
            O(M), where M is the maximum length of a song

        Time Complexity Analysis:
            For a given starting position, the function iterates through all subsequent notes, computing
            the pitch interval and traversing (or creating) a trie node per step. Each iteration performs
            O(1) work, resulting in a total of O(M) per call.

        Aux Space Complexity:
            O(1), as the function uses only constant auxiliary memory (loop counters and references).
            All trie nodes and child arrays are pre-allocated within the global trie structure.
        """
        node = self.root
        
        # The root represents single-note patterns
        if node.last_seen_song != song_idx:
            node.song_count += 1
            node.last_seen_song = song_idx
            if node.pattern_reference is None:
                node.pattern_reference = (song_idx, start)
        
        # Extend to longer interval-based patterns
        current_node = node
        for i in range(start + 1, len(notes)):
            # Compute interval difference between consecutive notes
            difference = notes[i] - notes[i - 1]
            index = difference + 25
            
            # Create child node if it is not already present
            if current_node.children[index] is None:
                child = TrieNode()
                child.parent = current_node
                child.parent_difference = difference
                current_node.children[index] = child

            # Move to child node
            current_node = current_node.children[index]

            # Update song count
            if current_node.last_seen_song != song_idx:
                current_node.song_count += 1
                current_node.last_seen_song = song_idx
                if current_node.pattern_reference is None:
                    current_node.pattern_reference = (song_idx, start)

    def extract_best_patterns(self):
        """
        Function Description:
            Performs a breadth-first traversal of the trie to identify and record the most frequent
            pattern for each possible pattern length. Each node is compared against the current
            best pattern of its depth and updated if it has higher frequency.

        Input:
            - None (uses self.root, self.M, and self.best_patterns from instance variables)

        Output:
            - None (populates self.best_patterns array in-place)

        Time Complexity:
            O(N*M), where N is the number of songs and M is the maximum length of a song

        Time Complexity Analysis:
            The trie contains at most O(N*M) nodes. Each node is visited exactly once during BFS.
            For every node, O(1) work is done to check and possibly update its best pattern record,
            and a constant time operation is performed to push its children into the queue.
            Therefore, the overall total time is O(N*M).

        Aux Space Complexity:
            O(N*M), where N is the number of songs and M is the maximum length of a song

        Aux Space Complexity Analysis:
            The BFS queue can hold up to O(N*M) nodes in the worst case and each queue entry stores
            a tuple (node, depth), which requires O(1) space per entry. Therefore, the total space 
            is O(N*M) * O(1) = O(N*M).
        """
        queue = deque()
        queue.append((self.root, 0))
        
        while queue:
            node, depth = queue.popleft()
            
            pattern_length = depth + 1
            if 1 <= pattern_length <= self.M:
                current_best = self.best_patterns[pattern_length]

                # Update best pattern if this node has higher song_count
                if current_best is None or node.song_count > current_best[0]:
                    self.best_patterns[pattern_length] = (
                        node.song_count, 
                        node.pattern_reference,
                        node
                    )

            # Add all child nodes
            for difference_index in range(51):
                child = node.children[difference_index]
                if child is not None:
                    queue.append((child, depth + 1))

    def get_path_to_node(self, node):
        """
        Function Description:
            Reconstructs the interval path from the trie root to a given node by traversing backward
            through parent pointers. This provides the sequence of pitch differences representing the
            pattern encoded by that node.

        Input:
            - node: Trie node whose interval path should be reconstructed

        Output:
            - path: List of integer interval differences representing the path from root to node

        Time Complexity:
            O(K), where K is the depth of the given node (pattern length - 1).

        Time Complexity Analysis:
            Each parent traversal step corresponds to one interval difference, with O(1) work per
            step. Total traversal requires O(K) iterations.

        Aux Space Complexity:
            O(K)

        Aux Space Complexity Analysis:
            It creates a path array proportional to the node's depth, K.
            Temporary variables and references are constant, giving O(K) total auxiliary space.
        """
        depth = 0
        current = node
        while current.parent is not None:
            depth += 1
            current = current.parent

        # Allocate list to hold interval differences
        path = [None] * depth

        # Trace back from the given node to the root, recording each interval along the way
        current = node
        idx = depth - 1
        while current.parent is not None:
            path[idx] = current.parent_difference
            current = current.parent
            idx -= 1
        
        return path

    def getFrequentPattern(self, pattern_length):
        """
        Function Description:
            Retrieves the most frequent transposition-invariant pattern of a given length.
            It reconstructs the representative note sequence using the stored best pattern node
            and its corresponding interval path.

        Input:
            - pattern_length: Integer representing the desired pattern length.

        Output:
            - List of note characters representing the most frequent pattern, or [] if no valid
              pattern exists for that length.

        Time Complexity:
            O(K), where K is equal to pattern_length

        Time Complexity Analysis:
            Performs constant-time lookup in self.best_patterns, followed by O(K) reconstruction 
            of the pattern by calling get_path_to_node() and reconstruct_pattern().
            Each operation processes one element (note or interval) per step, resulting in a total
            runtime that grows linearly with K.

        Aux Space Complexity:
            O(K), where K is equal to pattern_length

        Aux Space Complexity Analysis:
            It allocates temporary arrays to hold the reconstructed interval path and final note
            sequence, both of length K, leading to O(K) total auxiliary space usage.
        """
        # Validate pattern length and existence of best pattern
        if pattern_length < 2 or pattern_length > self.M or self.best_patterns[pattern_length] is None:
            return []

        # Retrieve stored info (frequency count, occurrence, node)
        count, occurrence, node = self.best_patterns[pattern_length]
        # Get interval path from root to node
        difference_path = self.get_path_to_node(node)

        # Ensure path length matches expected pattern length - 1
        if len(difference_path) != pattern_length - 1:
            return []
        
        return self.reconstruct_pattern(occurrence, difference_path)

    def reconstruct_pattern(self, occurrence, difference_path):
        """
        Function Description:
            Reconstructs the full note sequence from a given representative song occurrence and its
            corresponding interval difference path. The resulting pattern preserves transposition
            invariance and represents the most frequent melodic shape.

        Input:
            - occurrence: Tuple (song_idx, start_position) indicating where the pattern was first identified
            - difference_path: List of integer interval differences between consecutive notes

        Output:
            - result: List of characters representing the reconstructed note pattern, or an empty list
                      if occurrence is invalid or any note goes out of range.

        Time Complexity:
            O(K), where K is the length of the pattern.

        Time Complexity Analysis:
            The function iterates once through the interval path, performing O(1) arithmetic and range
            validation per step to compute each successive note. The total traversal requires O(K) iterations.

        Aux Space Complexity:
            O(K), where K is the length of the pattern.

        Aux Space Complexity Analysis:
            A temporary list of size K is allocated to store the reconstructed note sequence.
            All other variables occupy constant space, resulting in total auxiliary space O(K).
        """
        # If there is no valid representative, return empty
        if occurrence is None:
            return []
        
        song_idx, start_position = occurrence
        notes = self.songs[song_idx]
        
        # If start position is out of range, return empty
        if start_position >= len(notes):
            return []
        
        pattern_length = len(difference_path) + 1
        result = [None] * pattern_length

        # Initialize the pattern with the starting note converted to a letter
        current_note = notes[start_position]
        result[0] = chr(ord('a') + current_note)
        
        # Compute following notes by applying interval differences
        for i, difference in enumerate(difference_path):
            current_note += difference
            # Ensure valid note range ('a' to 'z')
            if current_note < 0 or current_note > 25:
                return []
            result[i + 1] = chr(ord('a') + current_note)
        
        return result
