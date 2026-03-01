"""
test_agent.py
=============
Run with:  python test_agent.py
No external libraries required — uses only the stdlib unittest module.

Tests cover:
  - Agent routing (correct intent detection)
  - Confidence values (within expected range)
  - Out-of-scope rejection
  - Extenuating, appeal, attendance, plagiarism, withdrawal paths
  - Retrieve scoring (sanity checks)
"""

import unittest
from agent import answer, generate_answer, is_domain_question, is_attendance_question, \
    is_appeal_question, is_extenuating_question, is_support_question, is_plagiarism_question, \
    is_withdrawal_question

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_context(policy="Test Policy", section="1.1 General", text="Students must follow all regulations."):
    return [{"policy": policy, "section": section, "text": text}]


def extract_confidence(response: str) -> int:
    import re
    match = re.search(r"Confidence:\s*(\d+)%", response)
    return int(match.group(1)) if match else -1


# ===========================================================================
# INTENT DETECTORS
# ===========================================================================

class TestIntentDetectors(unittest.TestCase):

    # --- Domain gate ---
    def test_domain_accepts_attendance(self):
        self.assertTrue(is_domain_question("What is the attendance policy?"))

    def test_domain_accepts_appeal(self):
        self.assertTrue(is_domain_question("Can I appeal my grade?"))

    def test_domain_accepts_plagiarism(self):
        self.assertTrue(is_domain_question("What happens if I plagiarise?"))

    def test_domain_rejects_weather(self):
        self.assertFalse(is_domain_question("What is the weather today?"))

    def test_domain_rejects_greeting(self):
        self.assertFalse(is_domain_question("Hello, how are you?"))

    def test_domain_rejects_cooking(self):
        self.assertFalse(is_domain_question("How do I make pasta?"))

    # --- Attendance ---
    def test_attendance_direct(self):
        self.assertTrue(is_attendance_question("what is the attendance policy"))

    def test_attendance_phrase_miss_classes(self):
        self.assertTrue(is_attendance_question("what happens if i miss classes"))

    def test_attendance_phrase_skip(self):
        self.assertTrue(is_attendance_question("can i skip lectures"))

    def test_attendance_no_false_positive_dismiss(self):
        # "dismiss" contains "miss" — must NOT match
        self.assertFalse(is_attendance_question("the committee will dismiss the complaint"))

    def test_attendance_absence(self):
        self.assertTrue(is_attendance_question("I had an absence last week"))

    # --- Appeals ---
    def test_appeal_direct(self):
        self.assertTrue(is_appeal_question("how do I appeal my mark"))

    def test_appeal_phrase_can_i(self):
        self.assertTrue(is_appeal_question("can I appeal my assessment result"))

    def test_appeal_grade(self):
        self.assertTrue(is_appeal_question("I want to appeal my grade"))

    # --- Extenuating ---
    def test_extenuating_illness(self):
        self.assertTrue(is_extenuating_question("I was ill during my exam"))

    def test_extenuating_missed_deadline(self):
        self.assertTrue(is_extenuating_question("I missed my deadline due to a family emergency"))

    def test_extenuating_couldnt_submit(self):
        self.assertTrue(is_extenuating_question("I couldn't submit my coursework"))

    def test_extenuating_bereavement(self):
        self.assertTrue(is_extenuating_question("I experienced bereavement"))

    # --- Support (wellbeing only) ---
    def test_support_pure_stress(self):
        self.assertTrue(is_support_question("I am really anxious and overwhelmed"))

    def test_support_mixed_with_policy_not_support(self):
        # stress + exam = should route to policy, not wellbeing
        self.assertFalse(is_support_question("I am stressed about my exam deadline"))

    # --- Plagiarism ---
    def test_plagiarism_direct(self):
        self.assertTrue(is_plagiarism_question("what counts as plagiarism"))

    def test_plagiarism_collusion(self):
        self.assertTrue(is_plagiarism_question("is sharing work considered collusion"))

    def test_plagiarism_misconduct(self):
        self.assertTrue(is_plagiarism_question("what is academic misconduct"))

    # --- Withdrawal ---
    def test_withdrawal_withdraw(self):
        self.assertTrue(is_withdrawal_question("I want to withdraw from my course"))

    def test_withdrawal_defer(self):
        self.assertTrue(is_withdrawal_question("can I defer my studies"))

    def test_withdrawal_drop_out(self):
        self.assertTrue(is_withdrawal_question("thinking about dropping out"))


# ===========================================================================
# ANSWER ROUTING
# ===========================================================================

class TestAnswerRouting(unittest.TestCase):

    # --- Out of scope ---
    def test_out_of_scope_weather(self):
        resp = answer("What is the weather today?", [])
        self.assertIn("Confidence: 0%", resp)
        self.assertIn("scope", resp.lower())

    def test_out_of_scope_cooking(self):
        resp = answer("How do I make risotto?", [])
        self.assertIn("Confidence: 0%", resp)

    # --- Attendance ---
    def test_attendance_response(self):
        resp = answer("What happens if I miss classes?", [])
        self.assertIn("Attendance and Engagement Policy", resp)
        conf = extract_confidence(resp)
        self.assertEqual(conf, 60)

    def test_attendance_no_fixed_limit(self):
        resp = answer("How many classes can I miss?", [])
        self.assertIn("does not define a fixed number", resp)

    # --- Appeals ---
    def test_appeal_response_contains_procedural(self):
        resp = answer("Can I appeal my exam result?", make_context())
        self.assertIn("procedural irregularity", resp)
        self.assertIn("Academic Appeals", resp)

    def test_appeal_confidence_in_range(self):
        resp = answer("I want to appeal my grade", make_context())
        conf = extract_confidence(resp)
        self.assertGreaterEqual(conf, 60)
        self.assertLessEqual(conf, 95)

    # --- Extenuating ---
    def test_extenuating_illness_response(self):
        resp = answer("I was ill and missed my exam", make_context(
            policy="Extenuating Circumstances Policy",
            section="2.1 Eligibility",
            text="Students who are ill may apply for extenuating circumstances."
        ))
        self.assertNotIn("Confidence: 0%", resp)

    def test_extenuating_missed_deadline(self):
        resp = answer("I couldn't submit my assignment due to a family emergency", make_context())
        self.assertNotIn("Confidence: 0%", resp)

    # --- Plagiarism ---
    def test_plagiarism_with_relevant_context(self):
        ctx = make_context(
            policy="Academic Integrity",
            section="3.1 Plagiarism",
            text="Plagiarism is presenting another's work as your own."
        )
        resp = answer("What is plagiarism?", ctx)
        self.assertNotIn("Confidence: 0%", resp)

    def test_plagiarism_no_context_returns_no_answer(self):
        resp = answer("What is plagiarism?", [])
        self.assertIn("cannot identify", resp.lower())

    # --- Withdrawal ---
    def test_withdrawal_with_context(self):
        ctx = make_context(
            policy="Withdrawal Policy",
            section="1.1 Process",
            text="Students wishing to withdraw must notify the Registry."
        )
        resp = answer("I want to withdraw from my course", ctx)
        self.assertNotIn("Confidence: 0%", resp)

    def test_withdrawal_no_context_returns_no_answer(self):
        resp = answer("I want to drop out", [])
        self.assertIn("cannot identify", resp.lower())

    # --- Wellbeing ---
    def test_wellbeing_pure_stress(self):
        resp = answer("I am really anxious and overwhelmed right now", [])
        self.assertIn("Student Support", resp)
        conf = extract_confidence(resp)
        self.assertEqual(conf, 40)

    def test_wellbeing_mixed_routes_to_policy(self):
        resp = answer("I'm stressed about my exam deadline, can I get an extension?", make_context())
        # Should NOT return the wellbeing response — should route to policy
        self.assertNotIn("I can't provide personal or wellbeing advice", resp)

    # --- Fallback: no answer ---
    def test_no_answer_in_domain_no_context(self):
        resp = answer("Tell me about university regulations", [])
        self.assertIn("cannot identify", resp.lower())

    # --- Backwards compatibility ---
    def test_generate_answer_alias(self):
        resp = generate_answer("What is the attendance policy?", [])
        self.assertIn("Attendance", resp)


# ===========================================================================
# CONFIDENCE SANITY CHECKS
# ===========================================================================

class TestConfidenceSanity(unittest.TestCase):

    def _conf(self, question, context=None):
        resp = answer(question, context or [])
        return extract_confidence(resp)

    def test_out_of_scope_is_zero(self):
        self.assertEqual(self._conf("What is 2+2?"), 0)

    def test_attendance_is_60(self):
        self.assertEqual(self._conf("What is the attendance policy?"), 60)

    def test_wellbeing_is_40(self):
        self.assertEqual(self._conf("I am really anxious and overwhelmed"), 40)

    def test_with_context_higher_than_without(self):
        ctx = make_context()
        conf_with    = self._conf("Can I appeal my mark?", ctx)
        conf_without = self._conf("Can I appeal my mark?", [])
        # no_answer gives 25, appeal with context gives 65+
        self.assertGreater(conf_with, conf_without)


# ===========================================================================
# RETRIEVE (smoke tests — requires docs/ folder to be present)
# ===========================================================================

class TestRetrieve(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import os
        cls.docs_available = os.path.isdir("docs") and any(
            f.endswith(".txt") for f in os.listdir("docs")
        )

    def test_retrieve_returns_list(self):
        if not self.docs_available:
            self.skipTest("docs/ folder not found — skipping retrieval tests")
        from retrieve import retrieve
        results = retrieve("attendance policy")
        self.assertIsInstance(results, list)

    def test_retrieve_result_has_required_keys(self):
        if not self.docs_available:
            self.skipTest("docs/ folder not found — skipping retrieval tests")
        from retrieve import retrieve
        results = retrieve("academic appeal")
        if results:
            self.assertIn("policy",  results[0])
            self.assertIn("section", results[0])
            self.assertIn("text",    results[0])

    def test_retrieve_max_results_respected(self):
        if not self.docs_available:
            self.skipTest("docs/ folder not found — skipping retrieval tests")
        from retrieve import retrieve
        results = retrieve("student support", max_results=3)
        self.assertLessEqual(len(results), 3)

    def test_retrieve_empty_question(self):
        if not self.docs_available:
            self.skipTest("docs/ folder not found — skipping retrieval tests")
        from retrieve import retrieve
        results = retrieve("")
        self.assertEqual(results, [])


# ===========================================================================
# MAIN
# ===========================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("UniC — Agent & Retrieval Test Suite")
    print("=" * 60)
    unittest.main(verbosity=2)
