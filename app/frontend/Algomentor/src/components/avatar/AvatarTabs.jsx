import { useState } from "react";

export default function AvatarTabs({ tabs }) {
  const [activeTab, setActiveTab] = useState(Object.keys(tabs)[0]);

  return (
    <div className="w-full">
      
      {/* Tab Buttons */}
      <div className="flex gap-2 mb-4">
        {Object.keys(tabs).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition
              ${
                activeTab === tab
                  ? "bg-slate-900 text-white"
                  : "bg-slate-200 text-slate-700 hover:bg-slate-300"
              }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-xl p-4 shadow">
        {tabs[activeTab]}
      </div>
    </div>
  );
}