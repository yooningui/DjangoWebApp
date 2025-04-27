from django.test import TestCase, Client
import coverage
from home.django_driver import DjangoFuzzer

class FuzzingTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cov = coverage.Coverage(branch=True, source=["home"])
        cls.cov.start()

    @classmethod
    def tearDownClass(cls):
        cls.cov.stop()
        cls.cov.save()
        super(FuzzingTest, cls).tearDownClass()

    def test_fuzz(self):
        # instantiate the fuzzer
        f = DjangoFuzzer(seed_path= "home/seed2.json", 
                         cov = self.cov,
                         client = Client())

        # run for 30 seconds
        stats = f.fuzz(timeout=300)


        print("🖐️  Fuzz stats:", stats)
        self.assertEqual(stats["failures"], 0, f"Found {stats['failures']} crashes")
        self.assertGreater(stats["unique_paths"], 0)
