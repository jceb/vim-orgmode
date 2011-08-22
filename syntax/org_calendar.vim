if version < 600
  syntax clear
elseif exists("b:current_syntax")
  finish
endif

syn case match

syn keyword orgCalMonth  January February March April May June July August September October November December
hi def link orgCalMonth       Comment

syn match orgCalYear /\d\d\d\d/
hi def link orgCalYear       Comment

syn keyword orgCalWeekDay    Mo Tu We Th Fr
hi def link orgCalWeekDay       Type

syn keyword orgCalWeekend    Sa Su
hi def link orgCalWeekend       Keyword
