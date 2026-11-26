// The server's own tools, no machine needed: the demo guide an agent follows, and what is running now.
import { connect } from "@cmdop/sdk";

const cmdop = connect(); // CMDOP_TOKEN, CMDOP_URL
const guide = await cmdop.showtime_guide({ language: "English" });
if (typeof guide !== "string" || guide.length < 200) throw new Error("showtime_guide gave no guide");
console.log(`showtime_guide: ${guide.length} characters; first line: ${guide.split("\n")[0]}`);
const now = await cmdop.tasks_list();
console.log(`tasks_list: ${now.tasks.length} started through cmdop, ${now.outside.length} machines with other processes`);
