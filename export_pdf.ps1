$ppt = New-Object -ComObject PowerPoint.Application
$pres = $ppt.Presentations.Open("C:\Users\momo\dev\dddsproject\docs\Precision_AI_CRM.pptx", 1, 0, 0)
$pres.SaveAs("C:\Users\momo\dev\dddsproject\docs\Precision_AI_CRM.pdf", 32)
$pres.Close()
$ppt.Quit()
Write-Output "PDF Exported Successfully"
