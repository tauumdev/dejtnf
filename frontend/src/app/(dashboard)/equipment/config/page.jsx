import { auth } from "../../../../auth";

export default async function ConfigEquipment() {
    const session = await auth();

    if (session?.user?.role === "admin") {
        return <p>You are an admin, welcome!</p>;
    }

    return <p>You are not authorized to view this page!</p>;
}
