param(
    $thres,
    $mode = "eval"
)

if($mode -eq "build") {
    & python .\evaluation\buildEval.py
} else {
    if (-not $thres) { $thres = 0.0 }
    & python .\evaluation\filter_system_output.py $thres
    & python .\evaluation\evaluate.py .\evaluation\system_output_filtered.json
}
