on run arguments
 if (count arguments) is not 1 and (count arguments) is not 2 then error "Pass the absolute path of the BRD .docx and an optional PDF output path."
 set documentPath to item 1 of arguments
 set targetName to name of (info for POSIX file documentPath)

 with timeout of 45 seconds
  tell application "Microsoft Word"
   -- Reopen the generated file instead of reusing an older document in memory.
   repeat with existingDoc in (get documents)
    if name of existingDoc is targetName then
     if saved of existingDoc is false then error "The BRD has unsaved Word edits. Save or close it before regenerating."
     close existingDoc saving no
    end if
   end repeat
   open file name documentPath
   set targetDoc to active document
   if (count of tables of contents of targetDoc) is not 1 then error "Expected one table of contents."

   repaginate targetDoc
   set include page numbers of table of contents 1 of targetDoc to true
   set right align page numbers of table of contents 1 of targetDoc to true
   set tab leader of table of contents 1 of targetDoc to tab leader dots
   update table of contents 1 of targetDoc
   repaginate targetDoc
   update page numbers table of contents 1 of targetDoc
   save targetDoc
   set contentsText to content of text object of table of contents 1 of targetDoc
   if (count arguments) is 2 then
    set exportPath to item 2 of arguments
    save as targetDoc file name exportPath file format format PDF
   end if
   return contentsText
  end tell
 end timeout
end run
