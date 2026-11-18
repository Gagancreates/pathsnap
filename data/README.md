# Data layout (not committed)

Place the provided dataset here so that:

```
data/
  train/<trip_id>/<trip_id>.{track,nodes,arcs,route}         # 80 trips
  student_test/<trip_id>/<trip_id>.{track,nodes,arcs,route}  # 10 trips
  eval_test/<trip_id>/...                                    # Laptop 1 only, given at evaluation
```

Symlinks work, e.g. `ln -s "/path/to/Student folder/train" data/train`.
Override the location with the `PATHSNAP_DATA` environment variable.
