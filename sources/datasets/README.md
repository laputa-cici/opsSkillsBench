# External Datasets Workspace

Use this directory for dataset metadata and small preprocessing notes. Large raw datasets should stay outside git unless explicitly approved.

Recommended layout:

```text
sources/datasets/
├── online-retail-ii/
│   ├── provenance.md
│   └── README.md
└── README.md
```

Commit small derived task slices under `tasks/<task-id>/environment/data/`, not here.

