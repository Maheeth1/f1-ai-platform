import pandas as pd
import catboost as cb

class AutoCatBoostRegressor(cb.CatBoostRegressor):
    def fit(self, X, y=None, **fit_params):
        if isinstance(X, pd.DataFrame):
            cat_cols = X.select_dtypes(include=['category', 'object']).columns.tolist()
            if cat_cols:
                fit_params['cat_features'] = cat_cols
        return super().fit(X, y, **fit_params)
