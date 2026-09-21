$word = New-Object -ComObject Word.Application
$doc = $word.Documents.Open("C:\Users\momo\dev\dddsproject\docs\user_manual.docx")
$doc.SaveAs("C:\Users\momo\dev\dddsproject\docs\user_manual.pdf", 17)
$doc.Close()
$word.Quit()
Write-Output "User Manual PDF Exported Successfully"
