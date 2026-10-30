"""Validate student scaffolds without replacing their TODOs with solutions."""
from pathlib import Path
import nbformat
ROOT=Path(__file__).resolve().parents[1]
def main():
    notebooks=sorted((ROOT/'projects').glob('*/project.ipynb'))
    assert len(notebooks)==5
    for p in notebooks:
        nb=nbformat.read(p,as_version=4);nbformat.validate(nb)
        exercises=tests=0
        for c in nb.cells:
            if c.cell_type!='code':continue
            assert not c.outputs and c.execution_count is None, f'Clear private outputs: {p}'
            compile(c.source,str(p),'exec')
            tags=c.metadata.get('tags',[])
            if any(t.startswith('exercise:') for t in tags):
                exercises+=1;assert 'TODO' in c.source and 'NotImplementedError' in c.source
            if 'test' in tags:tests+=1;assert 'assert ' in c.source
        assert exercises>=2 and tests>=2,(p,exercises,tests)
        assert len([c for c in nb.cells if c.cell_type=='markdown'])>=6
        print(f'{p.parent.name}: {len(nb.cells)} cells, {exercises} exercises, {tests} check cells')
    print('PASS: student scaffolds valid; this is not an execution of student solutions.')
if __name__=='__main__':main()
