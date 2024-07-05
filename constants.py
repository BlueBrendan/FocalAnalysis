folder_path = ''

focal_lengths_by_lens_dict = {} # {lens:{focalLength: count}}
lens_by_focal_length_dict = {} # {focal length:{lens: count}}

default_category_dropdown_selection = "All"
default_focal_length_ordering_dropdown_selection = "Focal Length"
default_lens_ordering_dropdown_selection = "Lens"
image_count_dropdown_selection = "Image Count"

focal_length_category = 'FocalLength'
lens_category = 'Lens'

graph_font = 'Kaiti'
progress_bar_font = f"{graph_font}, Arial, sans-serif"
progress_bar_style_sheet = f"""
    QProgressBar {{
        border: 1px solid grey;
        border-radius: 0px;
        background-color: #FFFFFF; /* Background color */
        text-align: center; /* Adjust text alignment */
        color: black;
        font: {progress_bar_font};
        font-size: 18px;
    }}
    QProgressBar::chunk {{
        background-color: #4CAF50; /* Green color */
    }}
    """
graph_padding_constant = 25