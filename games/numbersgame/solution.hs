module Solution where

import Foreign.C.Types

solution_hs :: Int -> Int -> Int
solution_hs a b = foldr1 lcm [a..b]

foreign export ccall solution_hs :: Int -> Int -> Int
