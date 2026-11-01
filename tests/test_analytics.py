import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from tourist_routes.analytics.cleaning import clean  # noqa: E402
from tourist_routes.analytics.converters import routes_to_dataframe  # noqa: E402
from tourist_routes.analytics.generate_dataset import generate  # noqa: E402
from tourist_routes.analytics.pipeline import run  # noqa: E402
from tourist_routes.core.sample_data import create_sample_routes  # noqa: E402


class CleaningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.raw_path = Path(self.tmp.name) / "raw.csv"
        self.raw = generate(str(self.raw_path))

    def tearDown(self):
        self.tmp.cleanup()

    def test_clean_removes_defects(self):
        df = clean(self.raw)
        self.assertEqual(df.drop(columns=["ratings_list"]).duplicated().sum(), 0)
        self.assertTrue(df["route_id"].is_unique)
        self.assertTrue(df["length_km"].between(0.1, 40000).all())
        self.assertEqual(df["price_eur"].isna().sum(), 0)
        self.assertTrue(all(c == c.strip() for c in df["country"].astype(str)))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df["date_added"]))

    def test_pipeline_writes_files(self):
        out = Path(self.tmp.name) / "out"
        df, grouped = run(self.raw_path, out, verbose=False)
        self.assertTrue((out / "processed_routes.csv").exists())
        reread = pd.read_csv(out / "grouped_country_type.csv")
        self.assertEqual(reread.shape, grouped.shape)
        self.assertEqual(pd.read_csv(out / "processed_routes.csv").shape[0], len(df))


class CoreIntegrationTests(unittest.TestCase):
    def test_pandas_matches_route_classes(self):
        routes = create_sample_routes()
        df = routes_to_dataframe(routes)
        for route, (_, row) in zip(routes, df.iterrows()):
            self.assertAlmostEqual(row["avg_rating"], route.average_rating(), places=2)
            self.assertAlmostEqual(row["duration_hours"], route.estimated_duration_hours(), places=2)


if __name__ == "__main__":
    unittest.main()
