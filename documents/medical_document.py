class MedicalDocument:
    def __init__(self):
        self.insurance_number = ""
        self.first_name = ""
        self.last_name = ""
        self.date_of_birth = ""
        self.jmbg = ""
        self.issuer = ""
        self.insurer_name = ""

    # def __repr__(self):
    #     return (
    #         "MedicalDocument(\n"
    #         f"  Insurance No: {self.insurance_number}\n"
    #         f"  Name: {self.first_name} {self.last_name}\n"
    #         f"  JMBG: {self.jmbg}\n"
    #         f"  DOB: {self.date_of_birth}\n"
    #         f"  Insurer name: {self.insurer_name}\n"
    #         ")"
    #     )
