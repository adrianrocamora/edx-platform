# -*- coding: utf-8 -*-
"""
Bok choy acceptance tests for LTI xblock
See also old lettuce tests in lms/djangoapps/courseware/features/lti.feature
"""
from ...fixtures.course import CourseFixture, XBlockFixtureDesc
from ...pages.lms.courseware import CoursewarePage, LTIContentIframe
from common.test.acceptance.pages.lms.tab_nav import TabNavPage
from common.test.acceptance.pages.lms.progress import ProgressPage
from common.test.acceptance.pages.lms.instructor_dashboard import (
    InstructorDashboardPage,
    StudentAdminPage,
    GradeBookPage
)
from ..helpers import UniqueCourseTest, auto_auth, select_option_by_text, select_option_by_value
import os


class TestLTIConusmer(UniqueCourseTest):
    """
    Base class for tests of LTI xblock in the LMS.
    """

    USERNAME = "STUDENT_TESTER"
    EMAIL = "student101@example.com"
    host = os.environ.get('BOK_CHOY_HOSTNAME', '127.0.0.1')

    def setUp(self):
        super(TestLTIConusmer, self).setUp()
        self.courseware_page = CoursewarePage(self.browser, self.course_id)
        self.lti_iframe = LTIContentIframe(self.browser, self.course_id)
        self.tab_nav = TabNavPage(self.browser)
        self.progress_page = ProgressPage(self.browser, self.course_id)
        self.instructor_dashboard_page = InstructorDashboardPage(self.browser, self.course_id)
        self.grade_book_page = GradeBookPage(self.browser)
        # Install a course
        display_name = "Test Course" + self.unique_id
        self.course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], display_name=display_name
        )
        # self.course_fix.visit()

    def test_lti_is_not_rendered(self):
        """
        Scenario: LTI component in LMS with no launch_url is not rendered
        Given the course has correct LTI credentials with registered Instructor
            the course has an LTI component with no_launch_url fields:
            Then I view the LTI and error is shown
        """
        metadata_advance_settings = "correct_lti_id:test_client_key:test_client_secret"
        metadata_lti_xblock = {
            'lti_id': '',
            'launch_url': '',
            'open_in_a_new_page': False
        }
        self.set_advance_settings(metadata_advance_settings)
        self.create_lti_xblock(metadata_lti_xblock)
        auto_auth(self.browser, self.USERNAME, self.EMAIL, True, self.course_id)
        self.courseware_page.visit()
        self.assertTrue(self.courseware_page.is_error_message_present())
        self.assertFalse(self.courseware_page.is_iframe_present())
        self.assertFalse(self.courseware_page.is_launch_url_present())

    def test_incorrect_lti_id_is_rendered(self):
        """
        Scenario: LTI component in LMS with incorrect lti_id is rendered incorrectly
        Given the course has correct LTI credentials with registered Instructor
            the course has an LTI component with incorrect_lti_id fields:
            Then I view the LTI but incorrect_signature warning is rendered
        """
        metadata_advance_settings = "test_lti_id:test_client_key:test_client_secret"
        metadata_lti_xblock = {
            'lti_id': 'incorrect_lti_id',
            'launch_url': 'http://{}:{}/{}'.format(self.host, '8765', 'correct_lti_endpoint'),
            'open_in_a_new_page': False
        }
        self.set_advance_settings(metadata_advance_settings)
        self.create_lti_xblock(metadata_lti_xblock)
        auto_auth(self.browser, self.USERNAME, self.EMAIL, True, self.course_id)
        self.courseware_page.visit()
        self.assertTrue(self.courseware_page.is_iframe_present())
        self.assertFalse(self.courseware_page.is_launch_url_present())
        self.assertFalse(self.courseware_page.is_error_message_present())
        self.courseware_page.go_to_lti_container()
        self.assertEqual("Wrong LTI signature", self.lti_iframe.lti_content)

    def test_incorrect_lti_credentials_is_rendered(self):
        """
        Scenario: LTI component in LMS with icorrect LTI credentials is rendered incorrectly
        Given the course has incorrect LTI credentials with registered Instructor
            the course has an LTI component with correct fields:
            I view the LTI but incorrect_signature warning is rendered
        """
        metadata_advance_settings = "test_lti_id:test_client_key:incorrect_lti_secret_key"
        metadata_lti_xblock = {
            'lti_id': 'correct_lti_id',
            'launch_url': 'http://{}:{}/{}'.format(self.host, '8765', 'correct_lti_endpoint'),
            'open_in_a_new_page': False
        }
        self.set_advance_settings(metadata_advance_settings)
        self.create_lti_xblock(metadata_lti_xblock)
        auto_auth(self.browser, self.USERNAME, self.EMAIL, True, self.course_id)
        self.courseware_page.visit()
        self.assertTrue(self.courseware_page.is_iframe_present())
        self.assertFalse(self.courseware_page.is_launch_url_present())
        self.assertFalse(self.courseware_page.is_error_message_present())
        self.courseware_page.go_to_lti_container()
        self.assertEqual("Wrong LTI signature", self.lti_iframe.lti_content)

    def test_lti_is_rendered_iframe(self):
        """
        Scenario: LTI component in LMS is correctly rendered in iframe
        Given the course has correct LTI credentials with registered Instructor
            the course has an LTI component with correct fields:
            I view the LTI and it is rendered in iframe
        """

        metadata_advance_settings = "correct_lti_id:test_client_key:test_client_secret"
        metadata_lti_xblock = {
            'lti_id': 'correct_lti_id',
            'launch_url': 'http://{}:{}/{}'.format(self.host, '8765', 'correct_lti_endpoint'),
            'open_in_a_new_page': False
        }

        self.set_advance_settings(metadata_advance_settings)
        self.create_lti_xblock(metadata_lti_xblock)
        auto_auth(self.browser, self.USERNAME, self.EMAIL, True, self.course_id)
        self.courseware_page.visit()
        self.assertTrue(self.courseware_page.is_iframe_present())
        self.assertFalse(self.courseware_page.is_launch_url_present())
        self.assertFalse(self.courseware_page.is_error_message_present())
        self.courseware_page.go_to_lti_container()
        self.assertEqual("This is LTI tool. Success.", self.lti_iframe.lti_content)

    def test_lti_graded_component_for_staff(self):
        """
        Scenario: Graded LTI component in LMS is correctly works for staff
        Given the course has correct LTI credentials with registered Instructor
            the course has an LTI component with correct fields:
            verify scores on progress and gradebook pages.
        """
        metadata_advance_settings = "correct_lti_id:test_client_key:test_client_secret"
        metadata_lti_xblock = {
            'lti_id': 'correct_lti_id',
            'launch_url': 'http://{}:{}/{}'.format(self.host, '8765', 'correct_lti_endpoint'),
            'open_in_a_new_page': False,
            'weight': 10,
            'graded': True,
            'has_score': True
        }
        EXPECTED_SCORES = [(5, 10)]
        self.set_advance_settings(metadata_advance_settings)
        self.create_lti_xblock(metadata_lti_xblock)
        auto_auth(self.browser, self.USERNAME, self.EMAIL, True, self.course_id)
        self.courseware_page.visit()
        self.courseware_page.go_to_lti_container()
        self.lti_iframe.submit_lti_answer('submit-button')
        self.assertIn("LTI consumer (edX) responded with XML content", self.lti_iframe.lti_content)
        self.lti_iframe.switch_to_default()
        self.tab_nav.go_to_tab('Progress')
        actual_scores = self.progress_page.scores("Test Chapter", "Test Section")
        self.assertEqual(actual_scores, EXPECTED_SCORES)
        self.assertEqual(['Overall Score', 'Overall Score\n1%'], self.progress_page.graph_overall_score())
        self.tab_nav.go_to_tab('Instructor')
        student_admin_section = self.instructor_dashboard_page.select_student_admin(StudentAdminPage)
        student_admin_section.click_grade_book_link()
        self.assertEqual("50", self.grade_book_page.see_value_in_the_grade_book('Homework 1 - Test Section', 1))
        self.assertEqual("1", self.grade_book_page.see_value_in_the_grade_book('Total', 1))

    def test_lti_switch_role(self):
        """
        Scenario: Graded LTI component in LMS is correctly works for staff
        Given the course has correct LTI credentials with registered Instructor
            the course has an LTI component with correct fields:
            verify scores on progress and gradebook pages.
        """
        metadata_advance_settings = "correct_lti_id:test_client_key:test_client_secret"
        metadata_lti_xblock = {
            'lti_id': 'correct_lti_id',
            'launch_url': 'http://{}:{}/{}'.format(self.host, '8765', 'correct_lti_endpoint'),
            'open_in_a_new_page': False,
            'has_score': True
        }
        self.set_advance_settings(metadata_advance_settings)
        self.create_lti_xblock(metadata_lti_xblock)
        auto_auth(self.browser, self.USERNAME, self.EMAIL, True, self.course_id)
        self.courseware_page.visit()
        self.assertTrue(self.courseware_page.is_iframe_present())
        self.assertFalse(self.courseware_page.is_launch_url_present())
        self.assertFalse(self.courseware_page.is_error_message_present())
        self.courseware_page.go_to_lti_container()
        self.assertEqual("This is LTI tool. Success.", self.lti_iframe.lti_content)
        self.assertEqual("Role: Instructor", self.lti_iframe.check_role)
        self.lti_iframe.switch_to_default()
        select_option_by_text(self.courseware_page.switch_role_selector, 'Learner')
        self.courseware_page.wait_for_ajax()
        self.assertTrue(self.courseware_page.is_iframe_present())
        self.assertFalse(self.courseware_page.is_launch_url_present())
        self.assertFalse(self.courseware_page.is_error_message_present())
        self.courseware_page.go_to_lti_container()
        self.assertEqual("This is LTI tool. Success.", self.lti_iframe.lti_content)
        self.assertEqual("Role: Student", self.lti_iframe.check_role)

    def test_lti_graded_component_for_learner(self):
        """
        Scenario: Graded LTI component in LMS is correctly works for staff
        Given the course has correct LTI credentials with registered Instructor
            the course has an LTI component with correct fields:
            verify scores on progress and gradebook pages.
        """
        metadata_advance_settings = "correct_lti_id:test_client_key:test_client_secret"
        metadata_lti_xblock = {
            'lti_id': 'correct_lti_id',
            'launch_url': 'http://{}:{}/{}'.format(self.host, '8765', 'correct_lti_endpoint'),
            'open_in_a_new_page': False,
            'weight': 10,
            'graded': True,
            'has_score': True
        }
        EXPECTED_SCORES = [(5, 10)]
        self.set_advance_settings(metadata_advance_settings)
        self.create_lti_xblock(metadata_lti_xblock)
        auto_auth(self.browser, self.USERNAME, self.EMAIL, False, self.course_id)
        self.courseware_page.visit()
        self.courseware_page.go_to_lti_container()
        self.lti_iframe.submit_lti_answer('submit-button')
        self.assertIn("LTI consumer (edX) responded with XML content", self.lti_iframe.lti_content)
        self.lti_iframe.switch_to_default()
        self.tab_nav.go_to_tab('Progress')
        actual_scores = self.progress_page.scores("Test Chapter", "Test Section")
        self.assertEqual(actual_scores, EXPECTED_SCORES)
        self.assertEqual(['Overall Score', 'Overall Score\n1%'], self.progress_page.graph_overall_score())

    def test_lti_v2_graded_component(self):
        """
        Scenario: Graded LTI component in LMS is correctly works for staff
        Given the course has correct LTI credentials with registered Instructor
            the course has an LTI component with correct fields:
            verify scores on progress and gradebook pages.
        """
        metadata_advance_settings = "correct_lti_id:test_client_key:test_client_secret"
        metadata_lti_xblock = {
            'lti_id': 'correct_lti_id',
            'launch_url': 'http://{}:{}/{}'.format(self.host, '8765', 'correct_lti_endpoint'),
            'open_in_a_new_page': False,
            'weight': 10,
            'graded': True,
            'has_score': True
        }
        EXPECTED_SCORES = [(8, 10)]
        problem_score = '(8.0 / 10.0 points)'
        self.set_advance_settings(metadata_advance_settings)
        self.create_lti_xblock(metadata_lti_xblock)
        auto_auth(self.browser, self.USERNAME, self.EMAIL, True, self.course_id)
        self.courseware_page.visit()
        self.courseware_page.go_to_lti_container()
        self.lti_iframe.submit_lti_answer("submit-lti2-button")
        self.assertIn("LTI consumer (edX) responded with HTTP 200", self.lti_iframe.lti_content)
        self.lti_iframe.switch_to_default()
        self.tab_nav.go_to_tab('Progress')
        actual_scores = self.progress_page.scores("Test Chapter", "Test Section")
        self.assertEqual(actual_scores, EXPECTED_SCORES)
        self.assertEqual(['Overall Score', 'Overall Score\n1%'], self.progress_page.graph_overall_score())
        self.tab_nav.go_to_tab('Instructor')
        student_admin_section = self.instructor_dashboard_page.select_student_admin(StudentAdminPage)
        student_admin_section.click_grade_book_link()
        self.assertEqual("80", self.grade_book_page.see_value_in_the_grade_book('Homework 1 - Test Section', 1))
        self.assertEqual("1", self.grade_book_page.see_value_in_the_grade_book('Total', 1))
        self.tab_nav.go_to_tab('Course')
        self.assertEqual(problem_score, self.courseware_page.see_elem_text('.problem-progress'))
        self.assertEqual("This is awesome.", self.courseware_page.see_elem_text('.problem-feedback'))

    def test_lti_delete_graded_component(self):
        """
        Scenario: Graded LTI component in LMS is correctly works for staff
        Given the course has correct LTI credentials with registered Instructor
            the course has an LTI component with correct fields:
            verify scores on progress and gradebook pages.
        """
        metadata_advance_settings = "correct_lti_id:test_client_key:test_client_secret"
        metadata_lti_xblock = {
            'lti_id': 'correct_lti_id',
            'launch_url': 'http://{}:{}/{}'.format(self.host, '8765', 'correct_lti_endpoint'),
            'open_in_a_new_page': False,
            'weight': 10,
            'graded': True,
            'has_score': True
        }
        EXPECTED_SCORES = [(0, 10)]
        problem_score = '(8.0 / 10.0 points)'
        self.set_advance_settings(metadata_advance_settings)
        self.create_lti_xblock(metadata_lti_xblock)
        auto_auth(self.browser, self.USERNAME, self.EMAIL, True, self.course_id)
        self.courseware_page.visit()
        self.courseware_page.go_to_lti_container()
        self.lti_iframe.submit_lti_answer("submit-lti2-button")
        self.assertIn("LTI consumer (edX) responded with HTTP 200", self.lti_iframe.lti_content)
        self.lti_iframe.switch_to_default()
        self.courseware_page.visit()
        self.assertEqual(problem_score, self.courseware_page.see_elem_text('.problem-progress'))
        self.assertEqual("This is awesome.", self.courseware_page.see_elem_text('.problem-feedback'))
        self.courseware_page.go_to_lti_container()
        self.lti_iframe.submit_lti_answer("submit-lti-delete-button")
        self.courseware_page.visit()
        self.assertEqual("(10.0 points possible)", self.courseware_page.see_elem_text('.problem-progress'))
        self.assertFalse(self.courseware_page.check_lti_component_no_elem('.problem-feedback'))
        self.tab_nav.go_to_tab('Progress')
        actual_scores = self.progress_page.scores("Test Chapter", "Test Section")
        self.assertEqual(actual_scores, EXPECTED_SCORES)
        self.assertEqual(['Overall Score', 'Overall Score\n0%'], self.progress_page.graph_overall_score())
        self.tab_nav.go_to_tab('Instructor')
        student_admin_section = self.instructor_dashboard_page.select_student_admin(StudentAdminPage)
        student_admin_section.click_grade_book_link()
        self.assertEqual("0", self.grade_book_page.see_value_in_the_grade_book('Homework 1 - Test Section', 1))
        self.assertEqual("0", self.grade_book_page.see_value_in_the_grade_book('Total', 1))

    def test_lti_hide_launch_shows_no_button(self):
        """
        Scenario: Graded LTI component in LMS is correctly works for staff
        Given the course has correct LTI credentials with registered Instructor
            the course has an LTI component with correct fields:
            verify scores on progress and gradebook pages.
        """
        metadata_advance_settings = "correct_lti_id:test_client_key:test_client_secret"
        metadata_lti_xblock = {
            'lti_id': 'correct_lti_id',
            'launch_url': 'http://{}:{}/{}'.format(self.host, '8765', 'correct_lti_endpoint'),
            'open_in_a_new_page': False,
            'hide_launch': True
        }
        self.set_advance_settings(metadata_advance_settings)
        self.create_lti_xblock(metadata_lti_xblock)
        auto_auth(self.browser, self.USERNAME, self.EMAIL, True, self.course_id)
        self.courseware_page.visit()
        self.assertFalse(self.courseware_page.check_lti_component_no_elem('.link_lti_new_window'))
        self.assertEqual("LTI (External resource)", self.courseware_page.see_elem_text('.problem-header'))

    def test_lti_hide_launch_shows_no_iframe(self):
        """
        Scenario: Graded LTI component in LMS is correctly works for staff
        Given the course has correct LTI credentials with registered Instructor
            the course has an LTI component with correct fields:
            verify scores on progress and gradebook pages.
        """
        metadata_advance_settings = "correct_lti_id:test_client_key:test_client_secret"
        metadata_lti_xblock = {
            'lti_id': 'correct_lti_id',
            'launch_url': 'http://{}:{}/{}'.format(self.host, '8765', 'correct_lti_endpoint'),
            'open_in_a_new_page': True,
            'hide_launch': True
        }
        self.set_advance_settings(metadata_advance_settings)
        self.create_lti_xblock(metadata_lti_xblock)
        auto_auth(self.browser, self.USERNAME, self.EMAIL, True, self.course_id)
        self.courseware_page.visit()
        self.assertFalse(self.courseware_page.check_lti_component_no_elem('.ltiLaunchFrame'))
        self.assertEqual("LTI (External resource)", self.courseware_page.see_elem_text('.problem-header'))

    def test_lti_button_text_correctly_displayed(self):
        """
        Scenario: Graded LTI component in LMS is correctly works for staff
        Given the course has correct LTI credentials with registered Instructor
            the course has an LTI component with correct fields:
            verify scores on progress and gradebook pages.
        """
        metadata_advance_settings = "correct_lti_id:test_client_key:test_client_secret"
        metadata_lti_xblock = {
            'lti_id': 'correct_lti_id',
            'launch_url': 'http://{}:{}/{}'.format(self.host, '8765', 'correct_lti_endpoint'),
            'button_text': 'Launch Application'
        }
        self.set_advance_settings(metadata_advance_settings)
        self.create_lti_xblock(metadata_lti_xblock)
        auto_auth(self.browser, self.USERNAME, self.EMAIL, True, self.course_id)
        self.courseware_page.visit()
        self.assertEqual("Launch Application", self.courseware_page.see_elem_text('.link_lti_new_window'))

    def test_lti_component_description_correctly_displayed(self):
        """
        Scenario: Graded LTI component in LMS is correctly works for staff
        Given the course has correct LTI credentials with registered Instructor
            the course has an LTI component with correct fields:
            verify scores on progress and gradebook pages.
        """
        metadata_advance_settings = "correct_lti_id:test_client_key:test_client_secret"
        metadata_lti_xblock = {
            'lti_id': 'correct_lti_id',
            'launch_url': 'http://{}:{}/{}'.format(self.host, '8765', 'correct_lti_endpoint'),
            'description': 'Application description'
        }
        self.set_advance_settings(metadata_advance_settings)
        self.create_lti_xblock(metadata_lti_xblock)
        auto_auth(self.browser, self.USERNAME, self.EMAIL, True, self.course_id)
        self.courseware_page.visit()
        self.assertEqual("Application description", self.courseware_page.see_elem_text('.lti-description'))

    def set_advance_settings(self, metadata_advance_settings):

        # Set value against advanced modules in advanced settings
        self.course_fix.add_advanced_settings({
            "advanced_modules": {"value": ["lti_consumer"]},
            'lti_passports': {"value": [metadata_advance_settings]}
        })

    def create_lti_xblock(self, metadata_lti_xblock):
        self.course_fix.add_children(
            XBlockFixtureDesc(category='chapter', display_name='Test Chapter').add_children(
                XBlockFixtureDesc(
                    category='sequential', display_name='Test Section', grader_type='Homework', graded=True
                ).add_children(
                    XBlockFixtureDesc(category='lti', display_name='LTI', metadata=metadata_lti_xblock).add_children(
                    )
                )
            )
        ).install()
