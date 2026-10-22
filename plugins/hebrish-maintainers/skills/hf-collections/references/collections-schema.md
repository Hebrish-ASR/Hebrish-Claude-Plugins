# Collections config schema

Read by `scripts/sync_collections.py --config <path>`. JSON. Example: `collections.example.json`.

```jsonc
{
  "org": "Hebrish",                       // Hugging Face organisation that owns the collections
  "exclude": ["Hebrish/Boxty-sherpa-onnx-int8"],   // never added to any collection
  "collections": [
    {
      "key": "jachnun",                   // short name for --only
      "title": "Jachnun",                 // matched against the Hub when "slug" is absent
      "slug": "Hebrish/jachnun-6ad7...",  // set once the collection exists; stops a title change creating a new one
      "description": "...",               // at most 150 characters (Hub limit)
      "auto": "audio-datasets",           // optional rule, see below
      "exclude": ["Hebrish/Parakeet-V2-Blend-All"],   // ids this collection's auto rule must skip
      "items": [                          // explicit items: [type, repo id] or [type, repo id, note]
        ["model", "Hebrish/Jachnun", "The model (.nemo). Access request."],
        ["space", "Hebrish/Jachnun-Demo"]
      ]
    }
  ]
}
```

`type` is `model`, `dataset` or `space` (the Hub also accepts `paper` and `collection`; the script
does not resolve those).

## `auto` rules

Computed from the org's own repos on every run:

| Rule | Adds |
| --- | --- |
| `audio-datasets` | org datasets with at least one audio file (`.wav .mp3 .flac .opus .ogg .m4a`) |
| `text-datasets` | org datasets with data files (`.jsonl .json .csv .parquet .txt .tsv .arrow`) and no audio |
| `spaces` | every org Space |
| `models` | every org model |

Datasets with no data files are skipped by every rule. Auto items carry no note; list a repo in
`items` as well to give it one (duplicates are merged).

## Behaviour

- Renamed or moved repos are resolved to their current id before comparing.
- Notes are only written when the config gives one; a config item without a note leaves the Hub's note
  alone.
- Items on the Hub that the config does not produce are `unmanaged`: reported, removed only with
  `--apply --prune`.
- Personal-account repos (not owned by `org`) go in only through explicit `items`.
