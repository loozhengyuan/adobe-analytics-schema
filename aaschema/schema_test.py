from unittest import TestCase

from aaschema.schema import generate_schema


class TestGenerateSchemaFunction(TestCase):
    """TestCase for generate_schema function"""

    def test_if_function_logs_error_if_output_format_is_invalid(self):
        """Test if function logs error if output format is invalid"""

        # Input/output scenarios
        headers = ["zip"]
        scenarios = (
            "0",    # string
            0,      # int
        )

        # Run subtest
        for arg in scenarios:
            with self.subTest(arg=arg):
                output = generate_schema(headers, style=arg)
                self.assertEqual(output, None)
