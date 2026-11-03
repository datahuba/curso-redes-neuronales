# Exporta cada .pptx de entregables/ a PDF usando PowerPoint.
# Uso: powershell -NoProfile -File tools/export_pdf.ps1 [carpeta] [carpetaPNG]
#  - carpetaPNG (opcional): además guarda cada diapositiva como PNG, para revisarlas.
param([string]$Dir = "entregables", [string]$PngDir = "")

$Dir = (Resolve-Path $Dir).Path
$app = New-Object -ComObject PowerPoint.Application
try {
    foreach ($f in Get-ChildItem $Dir -Filter *.pptx) {
        $pres = $app.Presentations.Open($f.FullName, $true, $false, $false)  # solo lectura, sin ventana
        $pdf = [IO.Path]::ChangeExtension($f.FullName, ".pdf")
        $pres.SaveAs($pdf, 32)                                               # 32 = ppSaveAsPDF
        if ($PngDir) {
            $out = Join-Path $PngDir $f.BaseName
            New-Item -ItemType Directory -Force $out | Out-Null
            foreach ($s in $pres.Slides) {
                $s.Export((Join-Path $out ("{0:D2}.png" -f $s.SlideIndex)), "PNG", 1600, 900)
            }
        }
        $pres.Close()
        Write-Output "PDF: $pdf"
    }
} finally {
    $app.Quit()
}
