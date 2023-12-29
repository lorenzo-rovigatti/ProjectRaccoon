from ..data.monomers import Monomer, Monomers
from ..functions import (
    generate_file,
    PDBtoXYZ,
    CheckMinimalDistance,
)


from unittest import TestLoader, TextTestRunner
from ...tests.unit.test_pdb_file import TestPdbFile
from questionary import text, select, confirm


def choose_option() -> str:
    return select(
        "Choose Function",
        choices=[
            "Create PDB File",
            "Check PDB File",
            "Convert PDB to XYZ File",
            "Check Minimal Distance",
            "Add Monomer",
            "Export JSON Monomer File",
            "Exit",
        ],
    ).ask()


def start_racoon(
    sequence_file: str,
    out_file: str,
    monomer_file: str,
    explicitbonds: bool,
    remove_duplicates: bool,
):
    option = choose_option()

    monomers = Monomers.from_json(monomer_file)

    while True:
        if option == "Create PDB File":
            generate_file(monomers, explicitbonds, sequence_file, out_file)

            option = choose_option()

        elif option == "Check PDB File":
            # Check Biopandas
            # try excpet (error catchen und error ausgeben) 
            suite = TestLoader().loadTestsFromTestCase(TestPdbFile)
            TextTestRunner().run(suite)
            option = choose_option()

        elif option == "Convert PDB to XYZ File":
            PDBtoXYZ(out_file)
            option = choose_option()

        elif option == "Check Minimal Distance":
            CheckMinimalDistance(out_file)
            option = choose_option()
        
        elif option == "Export JSON Monomer File":
            fpath = text("Enter JSON output filename").ask()
            if not fpath.split(".")[-1] == "json":
                print("Please specify a JSON output file.")
                option = choose_option()
            monomers.to_json(fpath)
            option = choose_option()

        elif option == "Add Monomer":
            name = text("Enter the name of the monomer").ask()
            resolution = select(
                "Choose resolution",
                choices=["atomistic", "united_atom", "coarse_grained"],
            ).ask()
            polymer = confirm("Is this a polymer?").ask()

            bs_file = text("Enter the name of the monomer's bs file: ").ask()
            atoms = Monomer.get_atoms_from_bs_file(bs_file)

            # Print atom list to console
            # Moritz muss das hier nochmal hübscher machen!

            [print(atom) for atom in atoms]

            linkC = text(f"Choose C-Terminus (1-{len(atoms)})").ask()
            linkN = text(f"Choose N-Terminus (1-{len(atoms)})").ask()
            link = [int(linkC), int(linkN)]

            ff_identifiers = list()
            for atom in atoms:
                ff_identifier = text(
                    f"Enter a force field Identifier for {atom[0]}' with the Number {atom[-1]}: "
                ).ask()
                ff_identifiers.append(ff_identifier)

            monmer = Monomer.create_monomer(
                name,
                resolution,
                polymer,
                link,
                atoms,
                ff_identifiers,
            )

            save = confirm("Do you want to save the monomer?").ask()

            monomers.add_monomer(monmer, save=save)

            option = choose_option()

        elif option == "Exit":
            return
