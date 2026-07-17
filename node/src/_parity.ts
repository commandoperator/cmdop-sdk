import { MachinesResource } from "./resources/machines";
import { SystemResource } from "./resources/system";

function toSnake(name: string): string {
  return name.replace(/[A-Z]/g, (character) => `_${character.toLowerCase()}`);
}

function methodsOf(resource: { prototype: object }): string[] {
  return Object.getOwnPropertyNames(resource.prototype)
    .filter((name) => name !== "constructor" && !name.startsWith("_"))
    .filter((name) => typeof Object.getOwnPropertyDescriptor(resource.prototype, name)?.value === "function")
    .map(toSnake)
    .sort();
}

export function actualSurface(): Record<string, string[]> {
  return { system: methodsOf(SystemResource), machines: methodsOf(MachinesResource) };
}
