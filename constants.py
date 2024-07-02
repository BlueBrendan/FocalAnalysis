folder_path = ''

focalLengthsByLens = {} # {lens:{focalLength: count}}
focalLengths = {} # {focal length: count}
lensByFocalLength = {} # {focal length:{lens: count}}
lensCount = {} # {lens: count}

lensModelExif = 42036
focalLengthIn35mmExif = 41989

defaultBarGraphColor = (0.122, 0.467, 0.706, 1.0)

defaultSelectionDropdownSelection = "All"
defaultFocalLengthOrderingDropdownSelection = "Focal Length"
defaultLensOrderingDropdownSelection = "Lens"
imageCountDropdownSelection = "Image Count"

# CATEGORIES
focalLengthCategory = 'FocalLength'
lensCategory = 'Lens'

focalLengthDistributionPaddingConstant = 20
lensDistributionGraphPaddingConstant = 90