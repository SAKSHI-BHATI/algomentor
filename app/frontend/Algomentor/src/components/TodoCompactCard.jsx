import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus } from "lucide-react";
import Card from "./Card";
import { cn } from "../lib/utils";

const TodoCompactCard = ({
  large,
  width = "w-full",
  height = "h-auto",}) => {
  const [tasks, setTasks] = React.useState([
    { id: 1, text: "Solve 2 Array problems", done: false },
    { id: 2, text: "Revise Graph BFS", done: false },
    { id: 3, text: "Review mistakes", done: true },
  ]);

  const [input, setInput] = React.useState("");
  const [openInput, setOpenInput] = React.useState(false);

  const toggleTask = (id) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, done: !t.done } : t))
    );
  };

  const addTask = () => {
    if (!input.trim()) return;
    setTasks((prev) => [
      ...prev,
      { id: Date.now(), text: input.trim(), done: false },
    ]);
    setInput("");
    setOpenInput(false);
  };

  return (
    <motion.div
      className={`${width} ${height}`}
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className={cn("shadow-sm h-full", large ? "p-6" : "p-4")} hoverable>
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-slate-900">
            📝 Today’s Plan
          </h3>

          <button
            onClick={() => setOpenInput((p) => !p)}
            className="p-1 rounded-md hover:bg-slate-100 transition"
          >
            <Plus className="w-4 h-4 text-slate-600" />
          </button>
        </div>

        {/* Tasks */}
        <div className="space-y-2">
          <AnimatePresence>
            {tasks.slice(0, 4).map((task) => (
              <motion.label
                key={task.id}
                layout
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="flex items-center gap-2 text-sm cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={task.done}
                  onChange={() => toggleTask(task.id)}
                  className="accent-indigo-600"
                />

                <span
                  className={cn(
                    "transition-all",
                    task.done && "line-through text-slate-400"
                  )}
                >
                  {task.text}
                </span>
              </motion.label>
            ))}
          </AnimatePresence>
        </div>

        {/* Input */}
        <AnimatePresence>
          {openInput && (
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mt-3 flex gap-2"
            >
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Add task..."
                className="flex-1 text-sm border rounded-md px-2 py-1 outline-none focus:ring-1 focus:ring-indigo-500"
              />
              <button
                onClick={addTask}
                className="text-sm px-2 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition"
              >
                Add
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </motion.div>
  );
};

export default TodoCompactCard;