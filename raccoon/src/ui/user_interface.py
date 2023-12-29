from ..data.monomers import Monomer, Monomers
from ..functions import (
    generate_file,
    PDBtoXYZ,
    CheckMinimalDistance,
)
from biopandas.pdb import PandasPdb
from rich.console import Console
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
            "Manage Monomers",
            "Exit",
        ],
    ).ask()

def manage_monomers() -> str:
    return select(
        "Choose Function",
        choices=[
            "Add Monomer",
            "Delete Monomer",
            "Print Monomers",
            "Export JSON Monomer File",
            "Return"]).ask()


def start_racoon(
    sequence_file: str,
    out_file: str,
    monomer_file: str,
    explicitbonds: bool,
    remove_duplicates: bool,
):
    option = choose_option()

    monomers = Monomers.from_json(monomer_file)

    # Use rich terminal to make it look a bit nicer :)
    console = Console()

    try:
        while True:


            if option == "Create PDB File":
                generate_file(monomers, explicitbonds, sequence_file, out_file)

                option = choose_option()

            elif option == "Check PDB File":

                try:
                    ppdb = PandasPdb().read_pdb(out_file)
                    console.print(ppdb.df["ATOM"], highlight=False)
                    console.print(f"Check Complete", style="bold green")
                except Exception as e:
                    console.print(f"Error: {e}", style="bold red")

                option = choose_option()

            elif option == "Convert PDB to XYZ File":
                PDBtoXYZ(out_file)
                option = choose_option()

            elif option == "Check Minimal Distance":
                CheckMinimalDistance(out_file)
                option = choose_option()

            elif option == "Manage Monomers":

                sec_option = manage_monomers()

                if sec_option == "Print Monomers":
                    console.print([f"{index} {monomer.name} {monomer.resolution}" for index, monomer in enumerate(monomers)])
                    sec_option = manage_monomers()

                elif sec_option == "Delete Monomer":

                    string_monomers = [[f"{index} {monomer.name} {monomer.resolution}" for index, monomer in enumerate(monomers)]][0]
                    monomer_select = select("Choose Monomer to remove",choices=string_monomers).ask()
                    monomer_identifier = int(monomer_select.strip()[0])

                    save = confirm(f"Do you want to remove the monomer {monomer_select}?").ask()
                    if save:
                        monomers.remove_monomer(monomer=monomers[monomer_identifier], save=save)
                        console.print(f"{monomer_select} was removed.", style="bold red")
                    if not save:
                        console.print("No monomers were removed.", style="bold red")

                elif sec_option == "Export JSON Monomer File":

                    fpath = text("Enter JSON output filename").ask()
                    if not fpath.split(".")[-1] == "json":
                        console.print("Please specify a JSON output file.", style="bold red")
                        return
                    monomers.to_json(fpath)
                    sec_option = manage_monomers()      

                elif sec_option == "Add Monomer":
                    name = text("Enter the name of the monomer").ask()
                    while name == "":
                        console.print("Please enter a valid name.", style="bold red")
                        name = text("Enter the name of the monomer").ask()
                    resolution = select(
                        "Choose resolution",
                        choices=["atomistic", "united_atom", "coarse_grained"],
                    ).ask()
                    polymer = confirm("Is this a polymer?").ask()

                    bs_file = text("Enter the name of the monomer's bs file: ").ask()
                    try:
                        atoms = Monomer.get_atoms_from_bs_file(bs_file)
                    except Exception as e:
                        console.print(f"Error: {e}", style="bold red")
                        sec_option = manage_monomers()

                    [console.print(f"Index: {index+1} Element Symbol: {atom[0]} Neighbors: {atom[4]}") for index, atom in enumerate(atoms)]

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

                    sec_option = manage_monomers()

                elif sec_option == "Return":
                    option = choose_option()


            elif option == "Exit":
                return
            
    except KeyboardInterrupt:
        console.print("Project RACCOON cancelled by user.", style="bold red")
        return
