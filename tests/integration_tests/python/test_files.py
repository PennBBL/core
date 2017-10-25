from api import files


def test_extension():
    assert files.guess_type_from_filename('example.pdf') == 'pdf'

def test_multi_extension():
    assert files.guess_type_from_filename('example.zip') == 'archive'
    assert files.guess_type_from_filename('example.gephysio.zip') == 'gephysio'

def test_nifti():
    assert files.guess_type_from_filename('example.nii') == 'nifti'
    assert files.guess_type_from_filename('example.nii.gz') == 'nifti'
    assert files.guess_type_from_filename('example.nii.x.gz') == None

def test_qa():
    assert files.guess_type_from_filename('example.png') == 'image'
    assert files.guess_type_from_filename('example.qa.png') == 'qa'
    assert files.guess_type_from_filename('example.qa') == None
    assert files.guess_type_from_filename('example.qa.png.unknown') == None

def test_unknown():
    assert files.guess_type_from_filename('example.unknown') == None

def test_insert_delete(as_drone):
    as_drone.post('/filetype', json={'_id': 'new', 'regex': '.*\.new$'})
    assert files.guess_type_from_filename('example.new') == 'new'
    as_drone.post('/filetype', json={'_id': 'new', 'regex': '.*\.new2$'})
    assert files.guess_type_from_filename('example.new') == None
    assert files.guess_type_from_filename('example.new2') == 'new'