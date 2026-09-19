$ppt = New-Object -ComObject PowerPoint.Application
$pres = $ppt.Presentations.Open("C:\Users\momo\dev\dddsproject\docs\demo.pptx", 1, 0, 0)
$pres.SaveAs("C:\Users\momo\dev\dddsproject\docs\demo.pdf", 32)
$pres.Close()
$ppt.Quit()
Write-Output "Demo PDF Exported Successfully"
