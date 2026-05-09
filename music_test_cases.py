from music_analyser import Analyser

# -------------------------------------------------------
# Test Case 1
# Basic example demonstrating repeated interval patterns
# -------------------------------------------------------
print("Test Case 1")
songs1 = ["cegec", "gdfhd", "cdfhd"]
analyser1 = Analyser(songs1)

print("K=2 =>", analyser1.getFrequentPattern(2))
print("K=3 =>", analyser1.getFrequentPattern(3))
print("K=4 =>", analyser1.getFrequentPattern(4))


# -----------------------------------------------------------------
# Test Case 2
# Multiple songs sharing strong transposition-invariant patterns
# -----------------------------------------------------------------
print("\nTest Case 2")
songs2 = ["abcdef", "bcdefg", "cdefgh"]

analyser2 = Analyser(songs2)

print("K=2 =>", analyser2.getFrequentPattern(2))
print("K=3 =>", analyser2.getFrequentPattern(3))
print("K=5 =>", analyser2.getFrequentPattern(5))


# ---------------------------------------------
# Test Case 3
# Edge case with invalid pattern lengths
# ---------------------------------------------
print("\nTest Case 3")
songs3 = ["abc", "xyz", "mnop"]

analyser3 = Analyser(songs3)

print("K=4 =>", analyser3.getFrequentPattern(4))
print("K=10 =>", analyser3.getFrequentPattern(10))