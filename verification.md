| # | Check | App shows | pandas gives | Match? |
|---|---|---|---|---|
| 1 | r for `age` vs `systolic_bp`, all participants | r = 0.463, n = 4,433 | r = 0.463, n = 4,433 | ✅ Yes |
| 2 | r for `bmi` vs `waist_cm`, all participants | r = 0.903, n = 4,433 | r = 0.903, n = 4,433 | ✅ Yes |
| 3 | r for `waist_cm` vs `hdl_chol`, all participants | r = -0.335, n = 4,433 | r = -0.335, n = 4,433 | ✅ Yes |
| 4 | r and n for `age` vs `systolic_bp`, **Female only** | r = 0.555, n = 2,263 | r = 0.555, n = 2,263 | ✅ Yes |
| 5 | r and n for `age` vs `systolic_bp`, **Male only** | r = 0.351, n = 2,170 | r = 0.351, n = 2,170 | ✅ Yes |
| 6 | With the filter set to Female, does the heatmap's `age`/`systolic_bp` square match row 4? | r = 0.56, n = 2,263 (heatmap rounds to 2 decimals) | r = 0.555, n = 2,263 | ✅ Yes |

