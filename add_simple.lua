
function string:split( inSplitPattern, outResults )
  if not outResults then
    outResults = { }
  end
  local theStart = 1
  local theSplitStart, theSplitEnd = string.find( self, inSplitPattern, theStart )
  while theSplitStart do
    table.insert( outResults, string.sub( self, theStart, theSplitStart-1 ) )
    theStart = theSplitEnd + 1
    theSplitStart, theSplitEnd = string.find( self, inSplitPattern, theStart )
  end
  table.insert( outResults, string.sub( self, theStart ) )
  return outResults
end

local uid = KEYS[1]

for j=1,#ARGV do
    local nscat = ARGV[j]:split(",") -- ns, site, cat, freq, recency
    local nscat_stub = "ns:" .. nscat[1] .. ":cat:" .. nscat[3]
    redis.call("SADD", "simple/" .. nscat_stub .. ":site:" .. nscat[2], uid)
    redis.call("SADD", "cat_site/" .. nscat_stub, nscat[2])
end

return #ARGV
