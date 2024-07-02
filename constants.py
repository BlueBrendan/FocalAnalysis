folder_path = ''

focalLengthsByLens = {} # {lens:{focalLength: count}}
focalLengths = {} # {focal length: count}
lensByFocalLength = {} # {focal length:{lens: count}}
lensCount = {} # {lens: count}

lensModelExif = 42036
focalLengthIn35mmExif = 41989

focalLengthChartTitle = 'Count By Focal Length'
focalLengthChartXLabel = 'Focal Length (mm)'
focalLengthChartYLabel = 'Count'
defaultBarGraphColor = (0.122, 0.467, 0.706, 1.0)

defaultSelectionDropdownSelection = "All"
defaultFocalLengthOrderingDropdownSelection = "Focal Length"
defaultLensOrderingDropdownSelection = "Lens"
imageCountDropdownSelection = "Image Count"

# Lens Ordering Dropdown Selection
lensOrderingDropdownSortByLens = "Lens"
lensOrderingDropdownSortByImageCount = "Image Count"

lensChartTitle = 'Count By Lens'
lensChartXLabel = 'Lens'
lensChartYLabel = 'Count'

# CATEGORIES
focalLengthCategory = 'FocalLength'
lensCategory = 'Lens'

paddingConstant = 20

barWidthByCategory = {
    focalLengthCategory: 400,
    lensCategory: 400
}

scrollbar_thresholds = {
    focalLengthCategory: 30,
    lensCategory: 6,
}

# Plot properties
plot_margins = {
    'focal_length_plot_x_spacing': 0.005,
    'lens_plot_x_spacing': 0.02
}

y_axis_multipliers = {
    'single_value': 2,
    'multi_value': 1.1
}

# Screen Properties
screen_height_percentage = 0.75